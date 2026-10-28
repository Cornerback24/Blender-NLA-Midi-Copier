"""Grease Pencil Dope Sheet copying."""

import bpy

from tests import midi_builder as mb
from tests.harness import blender_test
from tests.support import (
    add_filter,
    dope_property,
    expect,
    fresh_scene,
    load_midi,
    midi_file,
    midi_type,
    new_grease_pencil,
)


def _layer_with_frames(selected=(1, 10), extra_unselected=5):
    obj, data = new_grease_pencil()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    layer = data.layers.new("Lines")
    for number in selected:
        frame = layer.frames.new(number)
        frame.select = True
    if extra_unselected is not None:
        quiet = layer.frames.new(extra_unselected)
        quiet.select = False
    locked = data.layers.new("Locked")
    locked.lock = True
    locked_frame = locked.frames.new(1)
    locked_frame.select = True
    return obj, data, layer, locked


def _numbers(layer):
    return sorted(frame.frame_number for frame in layer.frames)


def _prepare(path, note="60", **fields):
    load_midi(path, midi_type("DOPESHEET"))
    prop = dope_property()
    prop.selected_note = str(note)
    prop.midi_frame_start = fields.pop("midi_frame_start", 100)
    note_action = prop.note_action_property
    for name, value in fields.items():
        setattr(note_action, name, value)
    return prop, note_action


@blender_test
def test_dope_sheet_copies_selected_frames_and_can_delete_sources():
    fresh_scene()
    _obj, _data, layer, locked = _layer_with_frames()
    _prepare(midi_file(mb.build_velocity_zero, "one.mid"))
    bpy.ops.nla_midi_copier.dope_sheet_copier()
    # Sources 1 and 10 map onto action start 100 with length 9.
    expect(_numbers(layer) == [1, 5, 10, 100, 109], _numbers(layer))
    expect(_numbers(locked) == [1], "locked layer was edited")

    fresh_scene()
    _obj, _data, layer, _locked = _layer_with_frames()
    _prop, note_action = _prepare(midi_file(mb.build_velocity_zero, "one.mid"))
    note_action.delete_source_keyframes = True
    bpy.ops.nla_midi_copier.dope_sheet_copier()
    expect(_numbers(layer) == [5, 100, 109], _numbers(layer))


@blender_test
def test_dope_sheet_sync_length_note_end_and_skip_overlaps():
    fresh_scene()
    _obj, _data, layer, _locked = _layer_with_frames(extra_unselected=None)
    _prop, note_action = _prepare(midi_file(mb.build_velocity_zero, "one.mid"))
    note_action.sync_length_with_notes = True
    note_action.scale_factor = 1
    bpy.ops.nla_midi_copier.dope_sheet_copier()
    # 500 ms is 12 frames. Source span 9 is scaled onto those 12 frames.
    expect(100 in _numbers(layer) and 112 in _numbers(layer), _numbers(layer))

    fresh_scene()
    _obj, _data, layer, _locked = _layer_with_frames(extra_unselected=None)
    _prop, note_action = _prepare(midi_file(mb.build_velocity_zero, "one.mid"), midi_frame_start=1)
    note_action.copy_to_note_end = True
    bpy.ops.nla_midi_copier.dope_sheet_copier()
    # Note length 12, so the pair starts at frame 13.
    expect(13 in _numbers(layer) and 22 in _numbers(layer), _numbers(layer))

    fresh_scene()
    _obj, _data, layer, _locked = _layer_with_frames(extra_unselected=None)
    _prop, note_action = _prepare(midi_file(mb.build_overlap_pair, "overlap.mid"), note="60")
    note_action.skip_overlaps = True
    bpy.ops.nla_midi_copier.dope_sheet_copier()
    numbers = _numbers(layer)
    expect(100 in numbers and 109 in numbers, numbers)
    expect(106 not in numbers, f"overlapping note was copied: {numbers}")


@blender_test
def test_dope_sheet_velocity_filter():
    fresh_scene()
    _obj, _data, layer, _locked = _layer_with_frames(extra_unselected=None)
    path = midi_file(lambda filename: mb.build_many_same_pitch(filename, 2, [100, 10]), "vel.mid")
    _prop, note_action = _prepare(path, note="60", midi_frame_start=50)
    note_action.add_filters = True
    add_filter(note_action, "note_velocity_filter", midi_type("DOPESHEET"),
               comparison_operator="equal_to", int_0_to_127=100)
    bpy.ops.nla_midi_copier.dope_sheet_copier()
    numbers = _numbers(layer)
    expect(50 in numbers and 59 in numbers, numbers)
    # The velocity-10 note starts one second later and would land on frames 74 and 83.
    expect(74 not in numbers and 83 not in numbers, numbers)


@blender_test
def test_dope_sheet_panel_poll():
    fresh_scene()
    from tests.runtime import addon
    panel = addon().DopeSheetMidiPanelModule.NLA_MIDI_COPIER_PT_dope_sheet_midi_panel
    window = bpy.context.window
    area = window.screen.areas[0]
    area.type = "DOPESHEET_EDITOR"
    region = next(region for region in area.regions if region.type == "WINDOW")
    space = area.spaces[0]
    space.mode = "GPENCIL"
    space.dopesheet.show_only_selected = True
    with bpy.context.temp_override(window=window, area=area, region=region):
        expect(panel.poll(bpy.context), "panel should show for Grease Pencil with only-selected")
        space.dopesheet.show_only_selected = False
        expect(not panel.poll(bpy.context), "panel hides until only-selected is on")
        space.mode = "DOPESHEET"
        expect(not panel.poll(bpy.context), "panel is Grease Pencil only")
