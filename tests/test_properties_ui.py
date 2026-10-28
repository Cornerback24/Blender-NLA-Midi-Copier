"""Properties, presets, file loading, load_post, registration, and translations."""

import bpy

from tests import midi_builder as mb
from tests.harness import blender_test
from tests.runtime import addon
from tests.support import (
    expect,
    fresh_scene,
    graph_property,
    load_midi,
    main_group,
    midi_file,
    midi_type,
    nla_property,
    temp_dir,
)


@blender_test
def test_properties_tempo_track_names_middle_c_and_note_search():
    fresh_scene()
    path = midi_file(mb.build_piano_format1, "piano.mid")
    reporter = load_midi(path, midi_type("NLA"))
    expect(reporter.messages == [], reporter.messages)
    prop = nla_property()
    expect(prop.midi_file == str(path), prop.midi_file)
    expect(abs(prop.tempo_settings.file_beats_per_minute - 120) < 0.01, prop.tempo_settings.file_beats_per_minute)
    expect(prop.tempo_settings.file_ticks_per_beat == 480, prop.tempo_settings.file_ticks_per_beat)
    expect(prop.on_overlap if False else prop.note_action_property.on_overlap == "BLEND",
           prop.note_action_property.on_overlap)
    expect(prop.note_action_property.blend_mode == "REPLACE", prop.note_action_property.blend_mode)

    track = next(item for item in prop.midi_track_properties if item.midi_track_name == "Piano")
    track.displayed_track_name = "Keys"
    loaded = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context)
    expect(loaded.get_displayed_track_name("Piano") == "Keys", loaded.track_list)

    prop.middle_c_note = "C5"
    notes = loaded.get_notes_list(bpy.context)
    prop.selected_midi_track = "Piano"
    notes = loaded.get_notes_list(bpy.context)
    c_note = next(item for item in notes if item[0] == "60")
    expect(c_note[1] == "C5", c_note[1])
    prop.note_search_string = "C5"
    expect(prop.selected_note == "60", prop.selected_note)
    prop.note_search_string = "C"
    expect(prop.selected_note == "60", "an ambiguous search should keep the current note")

    names = [item.midi_track_name for item in nla_property().midi_track_properties]
    expect("Empty" not in names, names)
    expect("Tempo" not in names, names)

    dup = midi_file(mb.build_duplicate_track_names, "dups.mid")
    load_midi(dup, midi_type("NLA"))
    names = sorted(item.midi_track_name for item in nla_property().midi_track_properties)
    expect(names == ["Piano", "Piano (2)"], names)

    blank = midi_file(mb.build_blank_track_name, "blank.mid")
    load_midi(blank, midi_type("NLA"))
    names = [item.midi_track_name for item in nla_property().midi_track_properties]
    expect(names == ["Track"], names)


@blender_test
def test_note_search_prefers_exact_match():
    from tests.runtime import addon as addon_module
    enums = [
        ("60", "C4", "C4", 60),
        ("61", "C#4", "C#4", 61),
        ("60b", "C4 (2)", "C4 with actions", 60),
    ]
    match = addon_module().PropertyUtils.find_matching_note(enums, "C4")
    expect(match[0] == "60", match)
    expect(addon_module().PropertyUtils.find_matching_note(enums, "C") is None, "C matches more than one note")
    expect(addon_module().PropertyUtils.find_matching_note(enums, "15") is None, "missing midi number")


@blender_test
def test_malformed_midi_file_reports_and_clears():
    fresh_scene()
    bad = temp_dir() / "bad.mid"
    bad.write_bytes(b"not midi")
    reporter = load_midi(bad, midi_type("NLA"))
    expect(nla_property().midi_file == "", nla_property().midi_file)
    expect(any(message.startswith("Could not load midi file:") for message in reporter.messages), reporter.messages)
    loaded = addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context)
    expect(loaded.midi_data is None, "failed load left parsed data behind")


@blender_test
def test_copy_midi_file_between_editors_and_relative_path():
    fresh_scene()
    path = midi_file(mb.build_format0, "fmt0.mid")
    load_midi(path, midi_type("NLA"))
    nla_property().midi_frame_start = 15
    nla_property().middle_c_note = "C3"
    nla_property().tempo_settings.use_file_tempo = False
    nla_property().tempo_settings.beats_per_minute = 90
    bpy.ops.ops.copy_midi_file_data(copy_from_data_type=midi_type("NLA"), copy_to_data_type=midi_type("GRAPH_EDITOR"))
    copied = graph_property()
    expect(copied.midi_file == str(path), copied.midi_file)
    expect(copied.midi_frame_start == 15, copied.midi_frame_start)
    expect(copied.middle_c_note == "C3", copied.middle_c_note)
    expect(copied.tempo_settings.use_file_tempo is False, "tempo flag was not copied")
    expect(abs(copied.tempo_settings.beats_per_minute - 90) < 0.01, copied.tempo_settings.beats_per_minute)
    same = addon().OperatorUtils.NLA_MIDI_COPIER_OT_copy_midi_file_data.compare_midi_file_data(
        bpy.context, midi_type("NLA"), midi_type("GRAPH_EDITOR"))
    expect(same, "compare_midi_file_data disagreed after a copy")

    blend = temp_dir() / "relative.blend"
    song = temp_dir() / "song.mid"
    mb.build_velocity_zero(song)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    nla_property()["midi_file"] = "//song.mid"
    addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context).update_midi_file(
        "//song.mid", True, context=bpy.context)
    notes = addon().midi_data.MidiDataUtil.get_notes(
        nla_property().selected_midi_track,
        addon().midi_data.get_midi_data(midi_type("NLA"), bpy.context))
    expect(len(notes) == 1 and notes[0].pitch == 60, [(note.pitch, note.start_time) for note in notes])


@blender_test
def test_filter_presets_round_trip():
    fresh_scene()
    note_action = nla_property().note_action_property
    note_action.add_filters = True
    data_type = midi_type("NLA")
    bpy.ops.nla_midi_copier.add_note_filter_group(midi_data_type=data_type)
    bpy.ops.nla_midi_copier.add_note_filter(midi_data_type=data_type, filter_group_index=0)
    created = note_action.note_filter_groups[0].note_filters[0]
    created.filter_type = "note_velocity_filter"
    created.comparison_operator = "equal_to"
    created.int_0_to_127 = 100
    bpy.ops.nla_midi_copier.add_note_filter_preset(midi_data_type=data_type)
    presets = main_group().midi_copier_data_common.filter_presets
    expect(len(presets) == 1, len(presets))
    expect(presets[0].note_filter_groups[0].note_filters[0].int_0_to_127 == 100, "preset did not copy the filter")
    created.int_0_to_127 = 10
    bpy.ops.nla_midi_copier.save_note_filter_preset(midi_data_type=data_type)
    expect(presets[0].note_filter_groups[0].note_filters[0].int_0_to_127 == 10, "save did not update the preset")
    bpy.ops.nla_midi_copier.delete_note_filter_preset(midi_data_type=data_type)
    expect(len(presets) == 0, "preset was not deleted")


@blender_test
def test_panels_preferences_and_translations():
    fresh_scene()
    mod = addon()
    panel_ids = [
        "NLA_MIDI_COPIER_PT_midi_panel",
        "NLA_MIDI_COPIER_PT_midi_instrument_panel",
        "NLA_MIDI_COPIER_PT_quick_copy_panel",
        "NLA_MIDI_COPIER_PT_midi_settings_panel",
        "NLA_MIDI_COPIER_PT_other_tools_panel",
        "NLA_MIDI_COPIER_PT_graph_editor_midi_panel",
        "NLA_MIDI_COPIER_PT_graph_editor_midi_settings_panel",
        "NLA_MIDI_COPIER_PT_dope_sheet_midi_panel",
        "NLA_MIDI_COPIER_PT_dope_sheet_midi_settings_panel",
    ]
    for panel_id in panel_ids:
        expect(hasattr(bpy.types, panel_id), f"{panel_id} is not registered")
    prefs = bpy.context.preferences.addons[mod.__package__].preferences
    other = mod.MidiPanelModule.NLA_MIDI_COPIER_PT_other_tools_panel
    prefs.show_nla_midi_other_tools_panel = False
    expect(not other.poll(bpy.context), "other tools panel ignored the preference")
    prefs.show_nla_midi_other_tools_panel = True
    expect(other.poll(bpy.context), "other tools panel stayed hidden")
    expect(bpy.ops.nla_midi_copier.delete_instrument.poll() is False, "delete should be disabled with no instrument")
    bpy.ops.nla_midi_copier.add_instrument()
    expect(bpy.ops.nla_midi_copier.delete_instrument.poll() is True, "delete stayed disabled")
    bpy.ops.nla_midi_copier.delete_instrument()

    view = bpy.context.preferences.view
    previous = view.language
    view.use_translate_interface = True
    view.language = "es"
    try:
        expect(mod.i18n.i18n.get_text(mod.i18n.i18n.COPY_ACTION_TO_SELECTED_OBJECTS)
               == "Copiar acción a objetos seleccionados",
               mod.i18n.i18n.get_text(mod.i18n.i18n.COPY_ACTION_TO_SELECTED_OBJECTS))
        expect(mod.i18n.i18n.get_text(mod.i18n.i18n.CHOOSE_MIDI_FILE_OP) == "Elegir archivo midi",
               mod.i18n.i18n.get_text(mod.i18n.i18n.CHOOSE_MIDI_FILE_OP))
        unchanged = mod.i18n.i18n.get_text(mod.i18n.i18n.COULD_NOT_COPY_ACTION_NO_NODE_TREE)
        expect(unchanged == "Could not copy the action because the target has no node tree.", unchanged)
    finally:
        view.language = previous

    # Headless Blender has no window to redraw. Registration and poll above cover the UI hooks.


@blender_test
def test_unregister_and_reregister():
    fresh_scene()
    mod = addon()
    try:
        mod.unregister()
        expect(not hasattr(bpy.types.Scene, "nla_midi_copier_main_property_group"), "scene property remained")
        expect(mod.on_load not in bpy.app.handlers.load_post, "load_post handler remained")
        expect(not hasattr(bpy.types, "NLA_MIDI_COPIER_PT_midi_panel"), "panel remained registered")
    finally:
        if not hasattr(bpy.types.Scene, "nla_midi_copier_main_property_group"):
            mod.register()
    expect(hasattr(bpy.types, "NLA_MIDI_COPIER_PT_midi_panel"), "re-register did not restore the panel")
    expect(mod.on_load in bpy.app.handlers.load_post, "re-register did not restore load_post")
    fresh_scene()
    expect(hasattr(bpy.context.scene, "nla_midi_copier_main_property_group"), "scene lost the property")


@blender_test
def test_load_post_reloads_each_scene_and_version():
    fresh_scene()
    first = midi_file(mb.build_velocity_zero, "scene-a.mid")
    second = midi_file(mb.build_format0, "scene-b.mid")
    load_midi(first, midi_type("NLA"))
    other = bpy.data.scenes.new("Second")
    original_scene = bpy.context.window.scene
    bpy.context.window.scene = other
    load_midi(second, midi_type("NLA"))
    bpy.context.window.scene = original_scene
    blend = temp_dir() / "reload.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    scenes = {scene.name: scene for scene in bpy.data.scenes}
    for scene in scenes.values():
        loaded = addon().midi_data.get_midi_data_for_scene(midi_type("NLA"), scene)
        expect(loaded.midi_data is not None, f"{scene.name} did not reload its midi file")
        generators = (scene.nla_midi_copier_main_property_group.graph_editor_midi_data_property
                      .note_action_property.keyframe_generators)
        expect(len(generators) == 1, f"{scene.name} graph generator count {len(generators)}")
    pitches = {}
    for scene in bpy.data.scenes:
        loaded = addon().midi_data.get_midi_data_for_scene(midi_type("NLA"), scene)
        track_name = scene.nla_midi_copier_main_property_group.nla_editor_midi_data_property.selected_midi_track
        if loaded.midi_data is not None and track_name in loaded.tracks_dict:
            pitches[scene.name] = sorted({note.pitch for note in loaded.tracks_dict[track_name].notes})
    expect(sorted(pitches.values()) == [[60], [60, 62]], pitches)
    version = bpy.context.scene.nla_midi_copier_main_property_group.midi_copier_version
    current = addon().addon_version()
    expect(current == (1, 2, 1), current)
    expect((version.major, version.minor, version.revision) == current,
           (version.major, version.minor, version.revision))
    expect(addon().on_load in bpy.app.handlers.load_post, "load_post handler is not registered")


@blender_test
def test_selecting_filter_preset_reloads_filters():
    """Selecting a preset copies it back onto the note action.

    This is last: on Blender 5.2+ the enum update crashes the process.
    """
    fresh_scene()
    note_action = nla_property().note_action_property
    data_type = midi_type("NLA")
    bpy.ops.nla_midi_copier.add_note_filter_group(midi_data_type=data_type)
    bpy.ops.nla_midi_copier.add_note_filter(midi_data_type=data_type, filter_group_index=0)
    created = note_action.note_filter_groups[0].note_filters[0]
    created.filter_type = "note_velocity_filter"
    created.int_0_to_127 = 80
    bpy.ops.nla_midi_copier.add_note_filter_preset(midi_data_type=data_type)
    created.int_0_to_127 = 1
    note_action.selected_note_filter_preset = "0"
    expect(created.int_0_to_127 == 80, created.int_0_to_127)
    graph_property().note_action_property.selected_note_filter_preset = "0"
    restored = graph_property().note_action_property.note_filter_groups[0].note_filters[0]
    expect(restored.filter_type == "note_velocity_filter" and restored.int_0_to_127 == 80,
           (restored.filter_type, restored.int_0_to_127))
