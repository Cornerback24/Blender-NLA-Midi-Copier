"""Graph Editor keyframe generation."""

import bpy

from tests import midi_builder as mb
from tests.harness import blender_test
from tests.runtime import addon
from tests.support import (
    add_filter,
    clear_keyframes,
    expect,
    fresh_scene,
    graph_generator_property,
    graph_property,
    keyframe_rows,
    load_midi,
    midi_file,
    midi_type,
    new_keyed_object,
    object_fcurves,
    run_graph_generator,
)


def _load_graph(path, track=None, note="60"):
    load_midi(path, midi_type("GRAPH_EDITOR"))
    prop = graph_property()
    if track is not None:
        prop.selected_midi_track = track
    prop.selected_note = str(note)
    return prop


def _generator(**values):
    generator = graph_generator_property()
    generator.property_type = values.pop("property_type", "note")
    generator.note_property = values.pop("note_property", "Pitch")
    generator.keyframe_placement_note_start = values.pop("keyframe_placement_note_start", True)
    generator.keyframe_placement_note_end = values.pop("keyframe_placement_note_end", False)
    generator.keyframe_placement_cc_data_change = values.pop("keyframe_placement_cc_data_change", False)
    generator.on_keyframe_overlap = values.pop("on_keyframe_overlap", "REPLACE")
    generator.on_note_overlap = values.pop("on_note_overlap", "include")
    generator.unit_type = values.pop("unit_type", "NONE")
    for name, value in values.items():
        setattr(generator, name, value)
    return generator


def _rows_after(path, track=None, note="60", keep_existing=False, **generator_values):
    fresh_scene()
    obj, fcurve = new_keyed_object()
    if keep_existing:
        fcurve.keyframe_points.insert(1, 42.0)
    _load_graph(path, track, note)
    _generator(**generator_values)
    # A second channel should receive the same keys.
    obj.keyframe_insert(data_path="location", frame=1, index=1)
    extra = object_fcurves(obj)[1]
    if not keep_existing:
        clear_keyframes(extra)
    else:
        clear_keyframes(extra)
        extra.keyframe_points.insert(1, 42.0)
    run_graph_generator(obj)
    return obj, keyframe_rows(fcurve), keyframe_rows(extra)


@blender_test
def test_graph_pitch_mapping_and_scale_filter():
    path = midi_file(mb.build_format0, "fmt0.mid")
    _obj, rows, extra = _rows_after(
        path, track="Solo", pitch_min="60", pitch_max="62", min_value=0.0, max_value=1.0)
    # Pitches 60, 61, 62. C4 maps to 0 and D4 maps to 1. Frames 1 and 13.
    expect(rows == [(1, 0.0), (13, 1.0)] or _close_rows(rows, [(1, 0.0), (13, 1.0)]), rows)
    expect(extra == rows, f"second fcurve {extra} != {rows}")

    path = midi_file(lambda filename: mb.build_chromatic_scale(filename, [60, 61], step_ticks=480), "chrom.mid")
    _obj, rows, _extra = _rows_after(
        path, pitch_min="60", pitch_max="61", min_value=0.0, max_value=1.0,
        scale_filter_type="in_scale", scale_filter_scale="C")
    expect(_frames(rows) == [1], f"in-scale should drop C#, got {rows}")
    _obj, rows, _extra = _rows_after(
        path, pitch_min="60", pitch_max="61", min_value=0.0, max_value=1.0,
        scale_filter_type="not_in_scale", scale_filter_scale="C")
    expect(_frames(rows) == [25], f"not-in-scale should keep C#, got {rows}")


@blender_test
def test_graph_only_notes_in_selected_track_changes_spacing():
    path = midi_file(lambda filename: mb.build_chromatic_scale(filename, [60, 64], step_ticks=480), "two.mid")
    _obj, rows, _extra = _rows_after(
        path, pitch_min="60", pitch_max="67", min_value=0.0, max_value=1.0,
        only_notes_in_selected_track=True)
    values = {frame: value for frame, value in rows}
    expect(abs(values[1] - 0.0) < 1e-4, rows)
    expect(abs(values[25] - 1.0) < 1e-4, rows)
    _obj, rows, _extra = _rows_after(
        path, pitch_min="60", pitch_max="67", min_value=0.0, max_value=1.0,
        only_notes_in_selected_track=False)
    values = {frame: value for frame, value in rows}
    expect(abs(values[25] - (4 / 7)) < 1e-3, f"unfiltered E4 should map to 4/7, got {rows}")


@blender_test
def test_graph_velocity_and_length_mapping():
    path = midi_file(lambda filename: mb.build_many_same_pitch(filename, 2, [40, 100]), "vel.mid")
    _obj, rows, _extra = _rows_after(
        path, note_property="Velocity", int_0_to_127_min=40, int_0_to_127_max=100,
        min_value=0.0, max_value=1.0)
    # The second note starts 1440 ticks (1.5 s) later, which is frame 37 at 24 fps.
    expect(_close_rows(rows, [(1, 0.0), (37, 1.0)]), rows)

    path = midi_file(mb.build_lengths, "lengths.mid")
    _obj, rows, _extra = _rows_after(
        path, note_property="Length", non_negative_min=12.0, non_negative_max=24.0,
        min_value=0.0, max_value=1.0, keyframe_placement_note_end=True,
        keyframe_placement_note_start=False)
    expect(_close_rows(rows, [(13, 0.0), (49, 1.0)]), rows)


@blender_test
def test_graph_keyframe_overlap_modes():
    path = midi_file(mb.build_velocity_zero, "one.mid")
    for mode, expected in (
            ("SKIP", [(1, 42.0)]),
            ("REPLACE", [(1, 0.0)]),
            ("PREVIOUS_FRAME", [(0, 0.0), (1, 42.0)]),
            ("NEXT_FRAME", [(1, 42.0), (2, 0.0)]),
    ):
        _obj, rows, _extra = _rows_after(
            path, keep_existing=True, pitch_min="60", pitch_max="60", min_value=0.0, max_value=1.0,
            on_keyframe_overlap=mode)
        expect(_close_rows(rows, expected), f"{mode}: {rows}")


@blender_test
def test_graph_note_overlap_skip_and_transition_limit():
    path = midi_file(mb.build_polyphonic_overlap, "poly.mid")
    _obj, rows, _extra = _rows_after(
        path, pitch_min="60", pitch_max="64", min_value=0.0, max_value=1.0, on_note_overlap="skip")
    expect(_frames(rows) == [1], f"overlapping E4 should be skipped, got {rows}")

    path = midi_file(mb.build_format0, "fmt0.mid")
    _obj, rows, _extra = _rows_after(
        path, track="Solo", pitch_min="60", pitch_max="62", min_value=0.0, max_value=1.0,
        keyframe_placement_note_start=True, keyframe_placement_note_end=False,
        limit_transition_length=True, transition_limit_frames=4, transition_offset_frames=0,
        transition_placement="start")
    # Note starts are 12 frames apart. The limited transition holds the next value from frame 5.
    expect(_close_rows(rows, [(1, 0.0), (5, 1.0), (13, 1.0)]), rows)


@blender_test
def test_graph_cc_keyframes_respect_first_frame():
    fresh_scene()
    path = midi_file(mb.build_cc_and_notes, "cc.mid")
    obj, fcurve = new_keyed_object()
    prop = _load_graph(path, note="60")
    prop.midi_frame_start = 10
    prop.note_action_property.midi_frame_offset = 5
    generator = _generator(property_type="cc_data", keyframe_placement_note_start=False,
                           keyframe_placement_cc_data_change=True, int_0_to_127_min=0,
                           int_0_to_127_max=127, min_value=0.0, max_value=1.0)
    addon().midi_data.get_midi_data(midi_type("GRAPH_EDITOR"), bpy.context).get_cc_data_list(bpy.context)
    generator.cc_type = "1"
    run_graph_generator(obj)
    rows = keyframe_rows(fcurve)
    # First Frame 10 plus offset 5. CC at 0 ms and 500 ms.
    expect(_close_rows(rows, [(15, 0.0), (27, 1.0)]), rows)


@blender_test
def test_graph_unit_type_selects_angle_values():
    path = midi_file(mb.build_format0, "fmt0.mid")
    _obj, rows, _extra = _rows_after(
        path, track="Solo", pitch_min="60", pitch_max="62", unit_type="ANGLE",
        min_value=5.0, max_value=9.0, min_value_angle=0.0, max_value_angle=2.0)
    expect(_close_rows(rows, [(1, 0.0), (13, 2.0)]), rows)


@blender_test
def test_graph_load_min_max_and_velocity_filter():
    fresh_scene()
    path = midi_file(mb.build_piano_format1, "piano.mid")
    _load_graph(path, track="Piano", note="60")
    generator = _generator(note_property="Pitch")
    bpy.ops.nla_midi_copier.load_min_max_from_midi_track()
    expect(generator.pitch_min == "60", generator.pitch_min)
    expect(generator.pitch_max == "67", generator.pitch_max)

    path = midi_file(lambda filename: mb.build_many_same_pitch(filename, 3, [10, 40, 90]), "vels.mid")
    fresh_scene()
    _load_graph(path, note="60")
    generator = _generator(note_property="Velocity")
    bpy.ops.nla_midi_copier.load_min_max_from_midi_track()
    expect(generator.int_0_to_127_min == 10, generator.int_0_to_127_min)
    expect(generator.int_0_to_127_max == 90, generator.int_0_to_127_max)

    fresh_scene()
    path = midi_file(mb.build_cc_and_notes, "cc.mid")
    _load_graph(path, note="60")
    generator = _generator(property_type="cc_data")
    addon().midi_data.get_midi_data(midi_type("GRAPH_EDITOR"), bpy.context).get_cc_data_list(bpy.context)
    generator.cc_type = "1"
    bpy.ops.nla_midi_copier.load_min_max_from_midi_track()
    expect(generator.int_0_to_127_min == 0 and generator.int_0_to_127_max == 127,
           (generator.int_0_to_127_min, generator.int_0_to_127_max))

    path = midi_file(lambda filename: mb.build_many_same_pitch(filename, 2, [100, 10]), "filter.mid")
    fresh_scene()
    obj, fcurve = new_keyed_object()
    _load_graph(path, note="60")
    _generator(note_property="Velocity", int_0_to_127_min=0, int_0_to_127_max=100,
               min_value=0.0, max_value=1.0)
    note_action = graph_property().note_action_property
    note_action.add_filters = True
    add_filter(note_action, "note_velocity_filter", midi_type("GRAPH_EDITOR"),
               comparison_operator="equal_to", int_0_to_127=100)
    run_graph_generator(obj)
    expect(_frames(keyframe_rows(fcurve)) == [1], keyframe_rows(fcurve))


def _frames(rows):
    return [frame for frame, _value in rows]


def _close_rows(actual, expected, tolerance=1e-3):
    if len(actual) != len(expected):
        return False
    for (frame, value), (expected_frame, expected_value) in zip(actual, expected):
        if frame != expected_frame or abs(value - expected_value) > tolerance:
            return False
    return True
