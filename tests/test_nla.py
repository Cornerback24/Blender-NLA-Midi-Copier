"""NLA copy, filters, instruments, quick copy, and transition tools."""

import bpy

from tests import midi_builder as mb
from tests.harness import blender_test
from tests.runtime import addon
from tests.support import (
    Reporter,
    SkipTest,
    activate_nla_track,
    add_filter,
    assert_strip,
    copy_nla,
    expect,
    fresh_scene,
    link,
    load_midi,
    make_action,
    make_object,
    midi_file,
    midi_type,
    new_grease_pencil,
    nla_property,
    nla_strips,
    nla_tracks,
    object_action,
    prepare_nla_copy,
    scene_compositor,
    slotted_actions,
    temp_dir,
    write_movie,
    write_wav,
)


def _one_note_file():
    return midi_file(mb.build_velocity_zero, "one-note.mid")


def _piano():
    return midi_file(mb.build_piano_format1, "piano.mid")


@blender_test
def test_nla_copy_places_strips_on_note_frames():
    fresh_scene()
    obj, action, _slot = object_action()
    prepare_nla_copy(obj, action, _piano(), note="60", track="Piano", on_overlap="SKIP")
    copy_nla()
    strips = nla_strips(obj)
    expect(len(strips) == 2, f"expected two C4 strips, got {len(strips)}")
    expect(len(nla_tracks(obj)) == 1, "non-overlapping notes stay on one track")
    expect(nla_tracks(obj)[0].name == "Midi", nla_tracks(obj)[0].name)
    # 0 ms and 1000 ms at 24 fps, first frame 1, action length 10.
    assert_strip(strips[0], 1, 11)
    assert_strip(strips[1], 25, 35)
    expect(strips[0].action == action, "strip does not use the selected action")


@blender_test
def test_nla_sync_scale_repeat_note_end_and_offsets():
    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, _one_note_file(), note="60")
    note_action.sync_length_with_notes = True
    note_action.scale_factor = 2
    note_action.sync_length_action_timing_mode = "scale_action_length"
    copy_nla()
    # 500 ms note is 12 frames. Scale 2 stretches the strip to 24 frames.
    assert_strip(nla_strips(obj)[0], 1, 25)
    expect(abs(nla_strips(obj)[0].scale - 2.4) < 0.05, f"scale {nla_strips(obj)[0].scale}")

    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, _one_note_file(), note="60")
    note_action.sync_length_with_notes = True
    note_action.scale_factor = 2
    note_action.sync_length_action_timing_mode = "repeat_action"
    copy_nla()
    strip = nla_strips(obj)[0]
    assert_strip(strip, 1, 25)
    expect(abs(strip.repeat - 2.4) < 0.05, f"repeat {strip.repeat}")
    expect(abs(strip.scale - 1) < 0.05, f"scale should stay 1 when repeating, got {strip.scale}")

    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, _one_note_file(), note="60")
    note_action.copy_to_note_end = True
    copy_nla()
    # Note length 12 frames, so the action starts at frame 13.
    assert_strip(nla_strips(obj)[0], 13, 23)

    fresh_scene()
    obj, action, _slot = object_action()
    prop, note_action = prepare_nla_copy(obj, action, _one_note_file(), note="60")
    prop.midi_frame_start = 10
    note_action.midi_frame_offset = -5
    copy_nla()
    assert_strip(nla_strips(obj)[0], 5, 15)


@blender_test
def test_nla_overlap_skip_blend_and_blend_types():
    fresh_scene()
    path = midi_file(mb.build_overlap_pair, "overlap.mid")
    obj, action, _slot = object_action()
    prepare_nla_copy(obj, action, path, note="60", on_overlap="SKIP")
    copy_nla()
    expect(len(nla_strips(obj)) == 1, f"skip should keep one strip, got {len(nla_strips(obj))}")
    assert_strip(nla_strips(obj)[0], 1, 11)

    for blend in ("REPLACE", "COMBINE", "ADD", "SUBTRACT", "MULTIPLY"):
        fresh_scene()
        obj, action, _slot = object_action()
        _prop, note_action = prepare_nla_copy(obj, action, path, note="60", on_overlap="BLEND")
        note_action.blend_mode = blend
        copy_nla()
        tracks = nla_tracks(obj)
        expect(len(tracks) == 2, f"{blend} should use two tracks, got {[track.name for track in tracks]}")
        expect(tracks[1].name == "Midi 2", tracks[1].name)
        upper = list(tracks[1].strips)[0]
        expect(upper.blend_type == blend, f"{blend} stored as {upper.blend_type}")
        expect(upper.extrapolation == "NOTHING", upper.extrapolation)
        assert_strip(list(tracks[0].strips)[0], 1, 11)
        assert_strip(upper, 7, 17)


@blender_test
def test_nla_duplicate_object_on_overlap():
    fresh_scene()
    path = midi_file(mb.build_overlap_pair, "overlap.mid")
    obj, action, _slot = object_action(make_object("Source"))
    before = {existing.name for existing in bpy.data.objects}
    prepare_nla_copy(obj, action, path, note="60", on_overlap="DUPLICATE_OBJECT")
    copy_nla()
    created = [bpy.data.objects[name] for name in bpy.data.objects.keys() if name not in before]
    expect(len(nla_strips(obj)) == 1, "original keeps the first note")
    expect(len(created) == 1, f"expected one duplicate, got {[item.name for item in created]}")
    expect(len(nla_strips(created[0])) == 1, "duplicate receives the overlapping note")
    assert_strip(nla_strips(created[0])[0], 7, 17)


@blender_test
def test_nla_duplicate_mesh_on_overlap():
    fresh_scene()
    path = midi_file(mb.build_overlap_pair, "overlap.mid")
    mesh = bpy.data.meshes.new("Shared")
    obj = link(bpy.data.objects.new("MeshHost", mesh))
    action, slot = make_action("MESH", name="MeshAction")
    load_midi(path, midi_type("NLA"))
    note_action = nla_property().note_action_property
    note_action.id_type = "Mesh"
    note_action.mesh = mesh
    note_action.action = action
    if slot is not None:
        note_action.action_slot_name = slot.name_display
    note_action.on_overlap = "DUPLICATE_OBJECT"
    note_action.nla_track_name = "Midi"
    nla_property().selected_note = "60"
    before = set(bpy.data.objects.keys())
    copy_nla()
    created = [bpy.data.objects[name] for name in bpy.data.objects.keys() if name not in before]
    expect(len(nla_strips(mesh)) == 1, "original mesh keeps one strip")
    expect(len(created) == 1, f"duplicates {[item.name for item in created]}")
    expect(created[0].data != mesh, "duplicate should not share the original mesh")
    expect(len(nla_strips(created[0].data)) == 1, "overlapping strip is on the duplicated mesh")


@blender_test
def test_nla_copy_to_selected_objects():
    fresh_scene()
    path = _one_note_file()
    action, slot = make_action("OBJECT", name="SharedAction")
    first = make_object("First")
    second = make_object("Second")
    ignored = make_object("Ignored")
    for obj in (first, second, ignored):
        obj.select_set(False)
    first.select_set(True)
    second.select_set(True)
    bpy.context.view_layer.objects.active = first
    load_midi(path, midi_type("NLA"))
    note_action = nla_property().note_action_property
    note_action.id_type = "Object"
    note_action.action = action
    note_action.copy_to_selected_objects = True
    note_action.nla_track_name = "Midi"
    note_action.on_overlap = "SKIP"
    if slot is not None:
        note_action.action_slot_name = slot.name_display
    nla_property().selected_note = "60"
    copy_nla()
    expect(len(nla_strips(first)) == 1 and len(nla_strips(second)) == 1, "both selected objects get a strip")
    expect(nla_strips(ignored) == [], "unselected object is left alone")
    expect(first.select_get() and second.select_get() and not ignored.select_get(), "selection is restored")


@blender_test
def test_nla_blank_track_name_uses_note_and_track():
    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, _piano(), note="60", track="Piano")
    note_action.nla_track_name = ""
    copy_nla()
    expect(nla_tracks(obj)[0].name == "C4 - Piano", nla_tracks(obj)[0].name)


@blender_test
def test_nla_custom_tempo_changes_strip_frame():
    fresh_scene()
    obj, action, _slot = object_action()
    prop, _note_action = prepare_nla_copy(obj, action, midi_file(mb.build_format0, "fmt0.mid"), note="62",
                                          track="Solo")
    prop.tempo_settings.use_file_tempo = False
    prop.tempo_settings.beats_per_minute = 60
    copy_nla()
    # Tick 480 at 60 bpm is 1 second, so the strip starts on frame 25 instead of 13.
    assert_strip(nla_strips(obj)[0], 25, 35)


@blender_test
def test_nla_action_slot_or_legacy_id_root():
    fresh_scene()
    obj = make_object("Slotted")
    if slotted_actions():
        action = bpy.data.actions.new("TwoSlots")
        first = action.slots.new(name="First", id_type="OBJECT")
        second = action.slots.new(name="Second", id_type="OBJECT")
        layer = action.layers.new("Layer")
        strip = layer.strips.new(type="KEYFRAME")
        for slot in (first, second):
            fcurve = strip.channelbag(slot, ensure=True).fcurves.new("location", index=0)
            fcurve.keyframe_points.insert(1, 0)
            fcurve.keyframe_points.insert(11, 1)
        _prop, note_action = prepare_nla_copy(obj, action, _one_note_file())
        note_action.action_slot_name = second.name_display
        copy_nla()
        copied = nla_strips(obj)[0]
        expect(copied.action_slot == second, f"strip slot {copied.action_slot} != {second.name_display}")
    else:
        action, _slot = make_action("OBJECT", name="Legacy")
        expect(action.id_root == "OBJECT", action.id_root)
        prepare_nla_copy(obj, action, _one_note_file())
        copy_nla()
        expect(len(nla_strips(obj)) == 1, "legacy action was not copied")


@blender_test
def test_nla_grease_pencil_action_matches_v3_slot():
    fresh_scene()
    _obj, data = new_grease_pencil()
    layer = data.layers.new("Ink")
    layer.opacity = 1.0
    layer.keyframe_insert("opacity", frame=1)
    layer.opacity = 0.25
    layer.keyframe_insert("opacity", frame=10)
    action = data.animation_data.action
    note_action = nla_property().note_action_property
    note_action.id_type = "Grease Pencil"
    expect(addon().MidiPropertiesModule.action_poll(note_action, action),
           "keyframed Grease Pencil action was rejected")
    if slotted_actions():
        slot_types = {slot.target_id_type for slot in action.slots}
        expected = "GREASEPENCIL" if bpy.app.version < (4, 3, 0) else "GREASEPENCIL_V3"
        expect(expected in slot_types, f"slots {slot_types}")
        decoy = bpy.data.actions.new("Annotation")
        decoy.slots.new(name="Ann", id_type="GREASEPENCIL")
        if bpy.app.version >= (4, 3, 0):
            expect(not addon().MidiPropertiesModule.action_poll(note_action, decoy),
                   "legacy GREASEPENCIL slot should not match Grease Pencil v3")
        else:
            expect(addon().MidiPropertiesModule.action_poll(note_action, decoy),
                   "4.2 Grease Pencil actions use GREASEPENCIL")
    note_action.greasepencil = data
    note_action.action = action
    note_action.nla_track_name = "GP"
    note_action.on_overlap = "SKIP"
    load_midi(_one_note_file(), midi_type("NLA"))
    nla_property().selected_note = "60"
    if slotted_actions():
        matches = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).matching_action_slots(note_action)
        expect(len(matches) >= 1, "no matching Grease Pencil slot")
        note_action.action_slot_name = matches[0].name_display
    copy_nla()
    expect(len(nla_strips(data)) == 1, "Grease Pencil data did not receive an NLA strip")


@blender_test
def test_nla_scene_compositor_and_material_node_tree():
    fresh_scene()
    scene = bpy.context.scene
    tree = scene_compositor(scene)
    action, slot = make_action("NODETREE", name="CompAction")
    load_midi(_one_note_file(), midi_type("NLA"))
    note_action = nla_property().note_action_property
    note_action.id_type = "Scene"
    note_action.scene = scene
    note_action.action = action
    note_action.nla_track_name = "Comp"
    note_action.on_overlap = "SKIP"
    nla_property().selected_note = "60"
    copy_nla()
    expect(len(nla_strips(tree)) == 1, "compositor node tree did not receive a strip")
    expect(nla_strips(scene) == [] or scene.animation_data is None or len(nla_tracks(scene)) == 0
           or all(strip.action != action for strip in nla_strips(scene)),
           "scene compositor action was stored on the scene instead of its node tree")

    fresh_scene()
    material = bpy.data.materials.new("Mat")
    if hasattr(material, "use_nodes"):
        material.use_nodes = True
    node_tree = material.node_tree
    expect(node_tree is not None, "material has no node tree")
    action, slot = make_action("NODETREE", name="MatNodes")
    load_midi(_one_note_file(), midi_type("NLA"))
    note_action = nla_property().note_action_property
    note_action.id_type = "Material"
    note_action.material = material
    note_action.action = action
    note_action.nla_track_name = "Nodes"
    note_action.on_overlap = "SKIP"
    nla_property().selected_note = "60"
    copy_nla()
    expect(len(nla_strips(node_tree)) == 1, "material node tree did not receive a strip")


@blender_test
def test_nla_node_tree_slot_is_listed_for_scene_and_material():
    """A NODETREE action selected for a Scene or Material needs its slot in the slot menu."""
    if not slotted_actions():
        fresh_scene()
        action, _slot = make_action("NODETREE", name="LegacyNodes")
        note_action = nla_property().note_action_property
        note_action.id_type = "Scene"
        expect(addon().MidiPropertiesModule.action_poll(note_action, action),
               "4.2 should accept a node-tree action for a scene")
        return
    fresh_scene()
    action, slot = make_action("NODETREE", name="SceneNodes")
    load_midi(_one_note_file(), midi_type("NLA"))
    note_action = nla_property().note_action_property
    note_action.id_type = "Scene"
    note_action.action = action
    matches = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).matching_action_slots(note_action)
    expect(any(candidate.target_id_type == "NODETREE" for candidate in matches),
           f"scene slot menu is {[candidate.target_id_type for candidate in matches]}, "
           f"action slot is {slot.target_id_type}")


@blender_test
def test_nla_missing_node_tree_warns():
    fresh_scene()
    texture = bpy.data.textures.new("Bare", type="CLOUDS")
    if getattr(texture, "node_tree", None) is not None:
        raise SkipTest("this Blender build gives every texture a node tree")
    action, slot = make_action("NODETREE", name="MissingNodes")
    load_midi(_one_note_file(), midi_type("NLA"))
    note_action = nla_property().note_action_property
    note_action.id_type = "Texture"
    note_action.texture = texture
    note_action.action = action
    note_action.on_overlap = "SKIP"
    nla_property().selected_note = "60"
    reporter = Reporter()
    notes = addon().midi_data.MidiDataUtil.get_notes(
        nla_property().selected_midi_track,
        addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context))
    addon().NLAMidiCopierModule.NoteActionCopier(note_action, bpy.context, None, operator=reporter).copy_notes(
        notes, "Midi", "60", bpy.context)
    expect(any("no node tree" in message for message in reporter.messages), reporter.messages)
    expect(not hasattr(texture, "animation_data") or texture.animation_data is None
           or nla_strips(texture) == [], "a strip was created without a node tree")


def _create_id_block(id_name):
    data = bpy.data
    if id_name == "Armature":
        return data.armatures.new("Arm")
    if id_name == "Brush":
        return data.brushes.new("BrushCopy")
    if id_name == "Camera":
        return data.cameras.new("Cam")
    if id_name == "Collection":
        return data.collections.new("Col")
    if id_name == "Curve":
        return data.curves.new("CurveData", type="CURVE")
    if id_name == "Grease Pencil":
        _obj, gp = new_grease_pencil("SweepGP")
        return gp
    if id_name == "Image":
        return data.images.new("Img", 1, 1)
    if id_name == "Key":
        mesh = data.meshes.new("ShapeMesh")
        obj = link(bpy.data.objects.new("ShapeObj", mesh))
        obj.shape_key_add(name="Basis")
        return mesh.shape_keys
    if id_name == "Lattice":
        return data.lattices.new("Lat")
    if id_name == "Light":
        return data.lights.new("Lamp", "POINT")
    if id_name == "Light Probe":
        return data.lightprobes.new("Probe", "SPHERE")
    if id_name == "Mask":
        return data.masks.new("Mask")
    if id_name == "Material":
        return data.materials.new("MatCopy")
    if id_name == "Metaball":
        return data.metaballs.new("Meta")
    if id_name == "Mesh":
        return data.meshes.new("MeshCopy")
    if id_name == "Movie Clip":
        movie = write_movie(temp_dir() / "clip.mp4")
        return data.movieclips.load(movie)
    if id_name == "Node Tree":
        return data.node_groups.new("Nodes", "ShaderNodeTree")
    if id_name == "Object":
        return make_object("IdObject")
    if id_name == "Paintcurve":
        if "animation_data" not in bpy.types.PaintCurve.bl_rna.properties:
            raise AssertionError(
                "PaintCurve is offered as an NLA id type but the RNA type has no animation_data")
        before = set(data.paint_curves.keys())
        try:
            result = bpy.ops.paintcurve.new()
        except RuntimeError as exc:
            raise SkipTest(f"paintcurve.new is unavailable headless: {exc}") from exc
        created = [curve for name, curve in data.paint_curves.items() if name not in before]
        if result != {"FINISHED"} or not created:
            raise SkipTest(f"paintcurve.new returned {result} and created {created}")
        return created[0]
    if id_name == "Palette":
        return data.palettes.new("Pal")
    if id_name == "Particle":
        return data.particles.new("Particles")
    if id_name == "Scene":
        return data.scenes.new("Extra")
    if id_name == "Sound":
        return data.sounds.load(write_wav(temp_dir() / "tone.wav"))
    if id_name == "Speaker":
        return data.speakers.new("Speaker")
    if id_name == "Text":
        return data.texts.new("Text")
    if id_name == "Texture":
        return data.textures.new("Tex", type="CLOUDS")
    if id_name == "Volume":
        return data.volumes.new("Vol")
    if id_name == "World":
        return data.worlds.new("World")
    raise AssertionError(f"no constructor for {id_name}")


def _copy_id_type(id_name):
    fresh_scene()
    block = _create_id_block(id_name)
    token = addon().midi_data.action_id_type(id_name)
    action, slot = make_action(token, name=id_name.replace(" ", "") + "Action")
    load_midi(_one_note_file(), midi_type("NLA"))
    note_action = nla_property().note_action_property
    note_action.id_type = id_name
    field = addon().midi_data.note_action_property_field_name(id_name)
    setattr(note_action, field, block)
    note_action.action = action
    if slot is not None:
        note_action.action_slot_name = slot.name_display
    note_action.nla_track_name = "Midi"
    note_action.on_overlap = "SKIP"
    nla_property().selected_note = "60"
    copy_nla()
    strips = nla_strips(block)
    expect(len(strips) == 1, f"{id_name} produced {len(strips)} strips")
    assert_strip(strips[0], 1, 11)


def _register_id_type_tests():
    for id_name in addon().midi_data.ID_PROPERTIES_DICTIONARY:
        def test(id_name=id_name):
            _copy_id_type(id_name)

        test.__name__ = "test_nla_copy_id_type_" + id_name.lower().replace(" ", "_")
        blender_test(test)


_register_id_type_tests()


@blender_test
def test_nla_filters_velocity_pitch_length_alternation_and_groups():
    fresh_scene()
    path = midi_file(lambda filename: mb.build_many_same_pitch(filename, 4, [100, 40, 10, 127]), "row.mid")
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, path, note="60", on_overlap="SKIP")
    note_action.add_filters = True
    group = note_action.note_filter_groups
    add_filter(note_action, "note_velocity_filter", midi_type("NLA"), comparison_operator="greater_than",
               int_0_to_127=40)
    copy_nla()
    # Velocities 100, 40, 10, 127. Greater than 40 keeps the first and the fourth.
    expect(len(nla_strips(obj)) == 2, f"velocity filter strips {[strip.frame_start for strip in nla_strips(obj)]}")

    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, _piano(), note="60", track="Piano", on_overlap="SKIP")
    note_action.add_filters = True
    add_filter(note_action, "note_pitch_filter", midi_type("NLA"), comparison_operator="greater_than",
               note_pitch="60")
    note_action.note_filter_groups[0].all_pitches = True
    copy_nla()
    # Piano pitches above 60 are E4 and G4. E starts at 0 ms, G at 500 ms.
    starts = sorted(strip.frame_start for strip in nla_strips(obj))
    expect(starts == [1, 13], f"pitch filter frames {starts}")

    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(
        obj, action, midi_file(mb.build_lengths, "lengths.mid"), note="60", on_overlap="SKIP")
    note_action.add_filters = True
    add_filter(note_action, "note_length_filter", midi_type("NLA"), comparison_operator="greater_than",
               time_unit="frames", non_negative_int=12)
    copy_nla()
    expect(len(nla_strips(obj)) == 1, "only the longer note should be copied")
    assert_strip(nla_strips(obj)[0], 25, 35)

    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, path, note="60", on_overlap="SKIP")
    note_action.add_filters = True
    add_filter(note_action, "note_alternation_filter", midi_type("NLA"), positive_int=2, positive_int_2=1)
    copy_nla()
    expect(len(nla_strips(obj)) == 2, f"alternation kept {len(nla_strips(obj))}")

    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, path, note="60", on_overlap="SKIP")
    note_action.add_filters = True
    add_filter(note_action, "note_velocity_filter", midi_type("NLA"), comparison_operator="equal_to",
               int_0_to_127=100)
    add_filter(note_action, "note_velocity_filter", midi_type("NLA"), group_index=1,
               comparison_operator="equal_to", int_0_to_127=10)
    copy_nla()
    expect(len(nla_strips(obj)) == 2, "either filter group should match")


@blender_test
def test_nla_filter_start_time():
    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(
        obj, action, midi_file(mb.build_format0, "fmt0.mid"), note="60", track="Solo", on_overlap="SKIP")
    note_action.add_filters = True
    add_filter(note_action, "note_start_time_frames", midi_type("NLA"), comparison_operator="greater_than",
               time_unit="frames", non_negative_int=10)
    note_action.note_filter_groups[0].all_pitches = True
    copy_nla()
    expect(len(nla_strips(obj)) == 1, "start-time filter should keep the later note")
    assert_strip(nla_strips(obj)[0], 13, 23)


@blender_test
def test_nla_filter_relative_start_time():
    fresh_scene()
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(
        obj, action, midi_file(mb.build_format0, "fmt0.mid"), note="60", track="Solo", on_overlap="SKIP")
    note_action.add_filters = True
    add_filter(note_action, "note_start_time_relative_frames", midi_type("NLA"),
               comparison_operator="greater_than", time_unit="seconds", non_negative_number=0.4)
    note_action.note_filter_groups[0].all_pitches = True
    copy_nla()
    expect(len(nla_strips(obj)) == 1, "relative start time should keep the note after 0.4 seconds")
    assert_strip(nla_strips(obj)[0], 13, 23)


@blender_test
def test_nla_overlap_filter_keeps_unoverlapped_note():
    fresh_scene()
    path = midi_file(mb.build_overlap_pair, "overlap.mid")
    obj, action, _slot = object_action()
    _prop, note_action = prepare_nla_copy(obj, action, path, note="60", on_overlap="BLEND")
    note_action.add_filters = True
    add_filter(note_action, "note_overlap_filter", midi_type("NLA"), comparison_operator="equal_to",
               comparison_operator2="equal_to", positive_int=1, positive_int_2=1)
    note_action.note_filter_groups[0].all_pitches = True
    copy_nla()
    starts = sorted(int(strip.frame_start) for strip in nla_strips(obj))
    # The two close C notes overlap as 10-frame actions. The later G does not.
    expect(starts == [49], f"overlap filter frames {starts}")


@blender_test
def test_nla_instrument_animate_transpose_and_all_instruments():
    fresh_scene()
    obj, action, slot = object_action(make_object("InstTarget"))
    other = make_object("OtherTarget")
    load_midi(_piano(), midi_type("NLA"))
    prop = nla_property()
    prop.selected_midi_track = "Piano"
    bpy.ops.nla_midi_copier.add_instrument()
    instrument = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).selected_instrument(bpy.context)
    instrument.name = "Piano"
    instrument.selected_note_id = "60"
    instrument.selected_midi_track = "Piano"
    instrument.copy_to_single_track = True
    instrument.nla_track_name = "Keys"
    instrument.instrument_midi_frame_offset = 10
    bpy.ops.nla_midi_copier.add_action_to_instrument()
    stored = instrument.notes[0].actions[0]
    stored.action = action
    stored.object = obj
    stored.on_overlap = "SKIP"
    stored.nla_track_name = ""
    if slot is not None:
        stored.action_slot_name = slot.name_display
    bpy.ops.nla_midi_copier.instrument_copier()
    strips = nla_strips(obj)
    expect(len(strips) == 2, f"instrument copied {len(strips)} strips")
    expect(nla_tracks(obj)[0].name == "Keys", nla_tracks(obj)[0].name)
    assert_strip(strips[0], 11, 21)

    instrument.transpose_filters = "transpose_all_leave_all_inclusive"
    stored.add_filters = True
    pitch_group = stored.note_filter_groups.add()
    pitch_filter = pitch_group.note_filters.add()
    pitch_filter.filter_type = "note_pitch_filter"
    pitch_filter.comparison_operator = "equal_to"
    pitch_filter.note_pitch = "60"
    extra = pitch_group.note_filters.add()
    extra.filter_type = "note_pitch_filter"
    extra.comparison_operator = "greater_than_or_equal_to"
    extra.note_pitch = "0"
    bpy.ops.nla_midi_copier.transpose_instrument(transpose_steps=12)
    expect(instrument.notes[0].note_id == 72, instrument.notes[0].note_id)
    expect(pitch_filter.note_pitch == "72", pitch_filter.note_pitch)
    expect(extra.note_pitch == "0", f"all-inclusive filter moved to {extra.note_pitch}")

    bpy.ops.nla_midi_copier.add_instrument()
    second = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).selected_instrument(bpy.context)
    second.selected_note_id = "64"
    second.selected_midi_track = "Piano"
    second.nla_track_name = "Second"
    bpy.ops.nla_midi_copier.add_action_to_instrument()
    second_action = second.notes[0].actions[0]
    second_action_data, second_slot = make_action("OBJECT", name="SecondAction")
    second_action.action = second_action_data
    second_action.object = other
    second_action.on_overlap = "SKIP"
    if second_slot is not None:
        second_action.action_slot_name = second_slot.name_display
    bpy.ops.nla_midi_copier.all_instrument_copier()
    expect(len(nla_strips(other)) >= 1, "animate-all skipped the second instrument")


@blender_test
def test_nla_quick_copy_by_name_path_and_instrument():
    fresh_scene()
    path = midi_file(lambda filename: mb.build_chromatic_scale(filename, [60, 64], step_ticks=480), "scale.mid")
    action, slot = make_action("OBJECT", name="Quick")
    low = make_object("C4_key")
    high = make_object("E4_key")
    low.location = (0, 0, 0)
    high.location = (1, 0, 0)
    load_midi(path, midi_type("NLA"))
    prop = nla_property()
    prop.selected_note = "60"
    note_action = prop.note_action_property
    note_action.id_type = "Object"
    note_action.action = action
    note_action.on_overlap = "SKIP"
    note_action.nla_track_name = "Quick"
    if slot is not None:
        note_action.action_slot_name = slot.name_display
    bulk = prop.bulk_copy_property
    bulk.quick_copy_tool = "copy_by_object_name"
    bulk.copy_by_name_type = "copy_by_note"
    bulk.selected_objects_only = True
    bulk.copy_to_instrument = False
    for obj in bpy.context.scene.objects:
        obj.select_set(False)
    low.select_set(True)
    high.select_set(True)
    bpy.ops.ops.nla_bulk_midi_copier()
    expect([int(strip.frame_start) for strip in nla_strips(low)] == [1],
           f"C4 object strips {[strip.frame_start for strip in nla_strips(low)]}")
    expect([int(strip.frame_start) for strip in nla_strips(high)] == [25],
           f"E4 object strips {[strip.frame_start for strip in nla_strips(high)]}")

    fresh_scene()
    action, slot = make_action("OBJECT", name="PathAction")
    left = make_object("Left")
    right = make_object("Right")
    left.location = (0, 0, 0)
    right.location = (1, 0, 0)
    curve = bpy.data.curves.new("PathCurve", type="CURVE")
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (0, 0, 0, 1)
    spline.points[1].co = (2, 0, 0, 1)
    path_obj = link(bpy.data.objects.new("Path", curve))
    load_midi(path, midi_type("NLA"))
    prop = nla_property()
    note_action = prop.note_action_property
    note_action.id_type = "Object"
    note_action.action = action
    note_action.on_overlap = "SKIP"
    if slotted_actions():
        matches = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).matching_action_slots(note_action)
        if matches:
            note_action.action_slot_name = matches[0].name_display
    bulk = prop.bulk_copy_property
    bulk.quick_copy_tool = "copy_along_path"
    bulk.bulk_copy_curve = path_obj
    bulk.bulk_copy_starting_note = "60"
    bulk.only_notes_in_selected_track = True
    bulk.scale_filter_type = "no_filter"
    bulk.copy_to_instrument = False
    # The note dropdown fills this list when the panel is drawn. The operator reads it directly.
    addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).get_notes_list(bpy.context)
    for obj in (left, right):
        obj.select_set(True)
    path_obj.select_set(False)
    bpy.context.view_layer.objects.active = left
    bpy.ops.ops.nla_bulk_midi_copier()
    expect(int(nla_strips(left)[0].frame_start) == 1, "first object along the path gets C4")
    expect(int(nla_strips(right)[0].frame_start) == 25, "second object gets E4")

    fresh_scene()
    action, slot = make_action("OBJECT", name="ToInst")
    host = make_object("Host")
    load_midi(_one_note_file(), midi_type("NLA"))
    prop = nla_property()
    note_action = prop.note_action_property
    note_action.id_type = "Object"
    note_action.object = host
    note_action.action = action
    if slotted_actions():
        matches = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).matching_action_slots(note_action)
        if matches:
            note_action.action_slot_name = matches[0].name_display
    bpy.ops.nla_midi_copier.add_instrument()
    prop.copy_to_instrument_selected_instrument = prop.selected_instrument_id
    prop.copy_to_instrument_selected_note_id = "60"
    prop.bulk_copy_property.quick_copy_tool = "copy_to_instrument"
    prop.bulk_copy_property.copy_to_instrument = True
    bpy.ops.ops.nla_bulk_midi_copier()
    instrument = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).selected_instrument_for_copy_to_id(
        bpy.context)
    copied = [action_prop for note in instrument.notes if note.note_id == 60 for action_prop in note.actions]
    expect(len(copied) == 1 and copied[0].action == action, "quick copy did not store the action on the instrument")
    expect(nla_strips(host) == [], "copy-to-instrument should not generate strips yet")


def _transition_pair():
    obj = make_object("TransitionHost")
    first, _slot = make_action("OBJECT", name="Leading", keys=((1, 0.0), (11, 1.0)))
    second, _slot = make_action("OBJECT", name="Trailing", keys=((1, 1.0), (11, 0.0)))
    animation = obj.animation_data_create()
    if slotted_actions():
        obj.animation_data.action = first
        obj.animation_data.action_slot = first.slots[0]
    track = animation.nla_tracks.new()
    track.name = "Base"
    leading = track.strips.new("leading", 1, first)
    trailing = track.strips.new("trailing", 40, second)
    if slotted_actions():
        leading.action_slot = first.slots[0]
        trailing.action_slot = second.slots[0]
    return obj, track


@blender_test
def test_nla_generate_and_delete_transitions():
    fresh_scene()
    obj, track = _transition_pair()
    tools = nla_property().other_tool_property
    tools.limit_transition_length = False
    tools.replace_transition_strips = False
    tools.keyframe_properties.interpolation = "LINEAR"
    tools.keyframe_properties.easing = "AUTO"
    for strip in track.strips:
        strip.select = True
    with activate_nla_track(obj, track):
        result = bpy.ops.nla_midi_copier.generate_transitions_operator()
    expect(result == {"FINISHED"}, result)
    transition = [strip for strip in track.strips if "Transition" in strip.name]
    expect(len(transition) == 1, [strip.name for strip in track.strips])
    assert_strip(transition[0], 11, 40)
    fcurves = addon().ActionUtils.get_action_util_object().get_action_strip_fcurves(transition[0])
    expect(len(fcurves) >= 1, "transition action has no fcurves")
    expect(fcurves[0].keyframe_points[0].interpolation == "LINEAR",
           fcurves[0].keyframe_points[0].interpolation)

    fresh_scene()
    obj, track = _transition_pair()
    tools = nla_property().other_tool_property
    tools.limit_transition_length = True
    tools.transition_limit_frames = 10
    tools.transition_offset_frames = 2
    tools.transition_placement = "start"
    tools.keyframe_properties.interpolation = "SINE"
    tools.keyframe_properties.easing = "EASE_IN"
    for strip in track.strips:
        strip.select = True
    with activate_nla_track(obj, track):
        bpy.ops.nla_midi_copier.generate_transitions_operator()
    transition = [strip for strip in track.strips if "Transition" in strip.name][0]
    assert_strip(transition, 13, 23)
    fcurves = addon().ActionUtils.get_action_util_object().get_action_strip_fcurves(transition)
    expect(fcurves[0].keyframe_points[0].interpolation == "SINE", fcurves[0].keyframe_points[0].interpolation)
    expect(fcurves[0].keyframe_points[0].easing == "EASE_IN", fcurves[0].keyframe_points[0].easing)

    tools.replace_transition_strips = True
    tools.transition_placement = "end"
    for strip in track.strips:
        strip.select = True
    with activate_nla_track(obj, track):
        bpy.ops.nla_midi_copier.generate_transitions_operator()
    transitions = [strip for strip in track.strips if "Transition" in strip.name]
    expect(len(transitions) == 1, f"replace left {len(transitions)} transitions")
    assert_strip(transitions[0], 28, 38)

    for strip in track.strips:
        strip.select = True
    with activate_nla_track(obj, track):
        bpy.ops.nla_midi_copier.delete_transitions_operator()
    expect([strip for strip in track.strips if "Transition" in strip.name] == [], "delete left a transition")
    expect(len(list(track.strips)) == 2, "action strips should remain")


@blender_test
def test_nla_transition_interpolations():
    interpolations = [item[0] for item in addon().MidiPropertiesModule.INTERPOLATIONS]
    for interpolation in interpolations:
        fresh_scene()
        obj, track = _transition_pair()
        tools = nla_property().other_tool_property
        tools.limit_transition_length = False
        tools.keyframe_properties.interpolation = interpolation
        tools.keyframe_properties.easing = "EASE_OUT"
        for strip in track.strips:
            strip.select = True
        with activate_nla_track(obj, track):
            bpy.ops.nla_midi_copier.generate_transitions_operator()
        transition = [strip for strip in track.strips if "Transition" in strip.name][0]
        fcurve = addon().ActionUtils.get_action_util_object().get_action_strip_fcurves(transition)[0]
        point = fcurve.keyframe_points[0]
        expect(point.interpolation == interpolation, f"{interpolation} stored as {point.interpolation}")
        if interpolation not in ("CONSTANT", "LINEAR", "BEZIER"):
            expect(point.easing == "EASE_OUT", f"{interpolation} easing {point.easing}")
