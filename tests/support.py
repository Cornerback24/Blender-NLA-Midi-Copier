"""Helpers for headless Blender tests. Import only after the add-on is enabled."""

from __future__ import annotations

import os
import struct
import wave
from pathlib import Path

import bpy

from tests import midi_builder as mb
from tests.runtime import addon


class SkipTest(Exception):
    """The test cannot run on this Blender build. Not an add-on failure."""


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def assert_close(actual, expected, tolerance=0.05, message=""):
    if abs(float(actual) - float(expected)) > tolerance:
        raise AssertionError(f"{message} expected {expected}, got {actual}".strip())


class Reporter:
    def __init__(self):
        self.messages = []

    def report(self, _level, message):
        self.messages.append(str(message))


def ensure_addon():
    """Re-enable the add-on after a factory reset.

    ``read_factory_settings`` clears enabled add-ons, which also removes the
    scene property and the ``load_post`` handler.
    """
    import addon_utils

    module = addon()
    name = module.__name__
    registered = hasattr(bpy.types.Scene, "nla_midi_copier_main_property_group")
    enabled = addon_utils.check(name)[1]
    if enabled and registered:
        return
    if enabled and not registered:
        addon_utils.disable(name)
    addon_utils.enable(name, default_set=True, persistent=True)


def fresh_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ensure_addon()
    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.fps_base = 1.0
    generators = (scene.nla_midi_copier_main_property_group.graph_editor_midi_data_property
                  .note_action_property.keyframe_generators)
    if len(generators) == 0:
        generators.add()
    return scene


def main_group(scene=None):
    scene = scene or bpy.context.scene
    return scene.nla_midi_copier_main_property_group


def nla_property(scene=None):
    return main_group(scene).nla_editor_midi_data_property


def dope_property(scene=None):
    return main_group(scene).dope_sheet_midi_data_property


def graph_property(scene=None):
    return main_group(scene).graph_editor_midi_data_property


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def load_midi(path, data_type, context=None):
    context = context or bpy.context
    reporter = Reporter()
    addon().OperatorUtils.load_midi_file(reporter, context, data_type, str(path))
    return reporter


def midi_type(name):
    return getattr(addon().midi_data.MidiDataType, name)


def make_object(name="Cube"):
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name + "Mesh"))
    link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    return obj


def slotted_actions():
    return bpy.app.version >= (4, 4, 0)


def make_action(id_type, name="Action", keys=((1, 0.0), (11, 1.0)), data_path="location", index=0):
    """Action whose frame range is 1..11 when ``keys`` is the default pair."""
    action = bpy.data.actions.new(name)
    slot = None
    if slotted_actions():
        slot = action.slots.new(name="Slot", id_type=id_type)
        layer = action.layers.new("Layer")
        strip = layer.strips.new(type="KEYFRAME")
        fcurve = strip.channelbag(slot, ensure=True).fcurves.new(data_path, index=index)
    else:
        action.id_root = id_type
        fcurve = action.fcurves.new(data_path, index=index)
    for frame, value in keys:
        fcurve.keyframe_points.insert(frame, value)
    return action, slot


def object_action(obj=None, name="LocationAction"):
    obj = obj or make_object()
    action, slot = make_action("OBJECT", name=name)
    return obj, action, slot


def action_fcurves(action, slot=None):
    if hasattr(action, "fcurves"):
        return list(action.fcurves)
    slot = slot or action.slots[0]
    return list(action.layers[0].strips[0].channelbag(slot).fcurves)


def nla_strips(id_block):
    animation = getattr(id_block, "animation_data", None)
    if animation is None:
        return []
    return [strip for track in animation.nla_tracks for strip in track.strips]


def nla_tracks(id_block):
    animation = getattr(id_block, "animation_data", None)
    if animation is None:
        return []
    return list(animation.nla_tracks)


def assert_strip(strip, start, end, tolerance=0.05):
    assert_close(strip.frame_start, start, tolerance, "frame_start")
    assert_close(strip.frame_end, end, tolerance, "frame_end")


def prepare_nla_copy(obj, action, midi_path, note="60", track=None, **fields):
    """Load a MIDI file and point the NLA panel at ``obj`` / ``action``."""
    load_midi(midi_path, midi_type("NLA"))
    prop = nla_property()
    note_action = prop.note_action_property
    note_action.id_type = "Object"
    note_action.object = obj
    note_action.action = action
    if track is not None:
        prop.selected_midi_track = track
    prop.selected_note = str(note)
    note_action.nla_track_name = fields.pop("nla_track_name", "Midi")
    note_action.on_overlap = fields.pop("on_overlap", "SKIP")
    for name, value in fields.items():
        setattr(note_action, name, value)
    if slotted_actions() and action is not None:
        matches = [slot for slot in action.slots if slot.target_id_type == "OBJECT"]
        if len(matches) == 1 and not note_action.action_slot_name:
            note_action.action_slot_name = matches[0].name_display
    return prop, note_action


def copy_nla():
    result = bpy.ops.nla_midi_copier.copier()
    expect(result == {"FINISHED"}, f"copier returned {result}")


def editor_area(editor_type):
    window = bpy.context.window
    area = next((candidate for candidate in window.screen.areas if candidate.type == "VIEW_3D"),
                window.screen.areas[0])
    area.type = editor_type
    region = next(region for region in area.regions if region.type == "WINDOW")
    return window, area, region


def override_editor(editor_type):
    window, area, region = editor_area(editor_type)
    return bpy.context.temp_override(window=window, area=area, region=region)


def activate_nla_track(obj, track, select_strips=True):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for candidate in obj.animation_data.nla_tracks:
        candidate.select = False
    track.select = True
    if select_strips:
        for strip in track.strips:
            strip.select = True
    return override_editor("NLA_EDITOR")


def new_grease_pencil(name="GP"):
    if bpy.app.version >= (5, 0, 0) or not hasattr(bpy.data, "grease_pencils_v3"):
        data = bpy.data.grease_pencils.new(name)
    else:
        data = bpy.data.grease_pencils_v3.new(name)
    obj = bpy.data.objects.new(name + "Obj", data)
    link(obj)
    return obj, data


def write_wav(path):
    path = str(path)
    with wave.open(path, "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(struct.pack("<" + "h" * 80, *([0] * 80)))
    return path


def write_movie(path):
    path = str(path)
    ffmpeg = None
    for candidate in ("ffmpeg", "/usr/bin/ffmpeg"):
        if os.path.exists(candidate) or candidate == "ffmpeg":
            ffmpeg = candidate
            break
    import shutil
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SkipTest("ffmpeg is not available, so no movie clip can be loaded")
    import subprocess
    completed = subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=16x16:d=0.2",
         "-pix_fmt", "yuv420p", path],
        check=False, capture_output=True, text=True)
    if completed.returncode != 0 or not os.path.exists(path):
        raise SkipTest(f"could not encode a movie clip: {completed.stderr}")
    return path


def ensure_node_tree(id_block):
    if getattr(id_block, "node_tree", None) is not None:
        return id_block.node_tree
    if hasattr(id_block, "use_nodes"):
        id_block.use_nodes = True
    tree = getattr(id_block, "node_tree", None)
    if tree is None:
        raise SkipTest(f"{id_block} has no node tree")
    return tree


def scene_compositor(scene):
    if hasattr(scene, "compositing_node_group"):
        if scene.compositing_node_group is None:
            tree = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
            scene.compositing_node_group = tree
        return scene.compositing_node_group
    if hasattr(scene, "use_nodes"):
        scene.use_nodes = True
    tree = getattr(scene, "node_tree", None)
    if tree is None:
        raise AssertionError("scene has neither node_tree nor compositing_node_group")
    return tree


def add_filter(note_action, filter_type, data_type, group_index=0, **values):
    if len(note_action.note_filter_groups) <= group_index:
        bpy.ops.nla_midi_copier.add_note_filter_group(midi_data_type=data_type, is_part_of_instrument=False)
    bpy.ops.nla_midi_copier.add_note_filter(
        midi_data_type=data_type, filter_group_index=group_index, is_part_of_instrument=False)
    note_filter = note_action.note_filter_groups[group_index].note_filters[-1]
    note_filter.filter_type = filter_type
    for name, value in values.items():
        setattr(note_filter, name, value)
    return note_filter


def keyframe_rows(fcurve):
    return [(int(round(key.co[0])), key.co[1]) for key in fcurve.keyframe_points]


def clear_keyframes(fcurve):
    for key in list(fcurve.keyframe_points):
        fcurve.keyframe_points.remove(key)


def object_fcurves(obj):
    action = obj.animation_data.action
    slot = getattr(obj.animation_data, "action_slot", None)
    return action_fcurves(action, slot)


def new_keyed_object():
    obj = make_object("Keyed")
    obj.keyframe_insert(data_path="location", frame=1, index=0)
    fcurve = object_fcurves(obj)[0]
    fcurve.select = True
    clear_keyframes(fcurve)
    return obj, fcurve


def run_graph_generator(obj):
    for fcurve in object_fcurves(obj):
        fcurve.select = True
        fcurve.hide = False
        fcurve.lock = False
    # The pitch-range filter reads the note list the MIDI panel fills in when it draws.
    loaded = addon().midi_data.get_midi_data(midi_type("GRAPH_EDITOR"), bpy.context)
    loaded.get_notes_list(bpy.context)
    with override_editor("GRAPH_EDITOR"):
        bpy.context.view_layer.objects.active = obj
        result = bpy.ops.nla_midi_copier.graph_editor_keyframe_generator()
    expect(result == {"FINISHED"}, f"graph generator returned {result}")


def graph_generator_property():
    return graph_property().note_action_property.keyframe_generators[0]


def temp_dir():
    # Keep fixtures outside Blender's temp directory. read_factory_settings clears that directory.
    root = Path("/tmp/nla-midi-copier-tests")
    root.mkdir(parents=True, exist_ok=True)
    return root


def midi_file(builder, name):
    path = temp_dir() / name
    builder(path)
    return path
