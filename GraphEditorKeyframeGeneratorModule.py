if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(GraphEditorMidiPropertiesModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteCollectionModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OperatorUtils)
else:
    from . import midi_data
    from . import PitchUtils
    from . import GraphEditorMidiPropertiesModule
    from . import NoteCollectionModule
    from . import OperatorUtils

import bpy
from collections import defaultdict
from typing import List
from .midi_data import MidiDataType
from .NoteCollectionModule import NoteCollection, NoteCollectionMetaData, NoteCollectionOverlapStrategy, \
    NoteCollectionFilter


def existing_keyframe_map(keyframes):
    """
    :param keyframes: list of keyframes
    :return: map of frame to list of keyframes (there will most likely only be one keyframe per frame, but there is a
     possibility of multiple keyframes on the same frame)
    """
    frames_to_keyframes = defaultdict(list)
    for keyframe in keyframes:
        frames_to_keyframes[keyframe.co[0]].append(keyframe)
    return frames_to_keyframes


def add_keyframe(keyframe_points, existing_keyframes, frame, keyframe_value, overlap_mode):
    def add(frame_number):
        keyframe_points.add(1)
        added_keyframe = keyframe_points[-1]
        added_keyframe.co[0] = frame_number
        added_keyframe.co[1] = keyframe_value

    if overlap_mode == 'SKIP':
        if not existing_keyframes[frame]:
            add(frame)
    elif overlap_mode == 'PREVIOUS_FRAME':
        if not existing_keyframes[frame]:
            add(frame)
        elif not existing_keyframes[frame - 1]:
            add(frame - 1)
    elif overlap_mode == 'NEXT_FRAME':
        if not existing_keyframes[frame]:
            add(frame)
        elif not existing_keyframes[frame + 1]:
            add(frame + 1)
    else:  # replace
        add(frame)


note_property_definitions = \
    {"Pitch": (lambda analyzed_note: analyzed_note.note.pitch, "pitch_min", "pitch_max"),
     "Length": (lambda analyzed_note: analyzed_note.note_length_frames, "non_negative_min", "non_negative_max"),
     "Velocity": (lambda analyzed_note: analyzed_note.note.velocity, "int_0_to_127_min", "int_0_to_127_max")}


def value_from_analyzed_note(note_property: str, analyzed_note):
    return note_property_definitions[note_property][0](analyzed_note)


def get_note_collection(loaded_midi_data, context, graph_editor_note_action_property,
                        keyframe_generator_property):
    graph_editor_midi_data_property = context.scene.graph_editor_midi_data_property
    notes = midi_data.MidiDataUtil.get_notes(
        loaded_midi_data.get_track_id(context),
        loaded_midi_data)
    note_collection_meta_data = NoteCollectionMetaData(
        loaded_midi_data, context.scene.render.fps,
        graph_editor_midi_data_property.midi_frame_start + graph_editor_note_action_property.midi_frame_offset,
        False, None, None)
    overlap_strategy = NoteCollectionOverlapStrategy(False, False, False)
    note_id = loaded_midi_data.get_note_id(context)
    note_collection_filter = NoteCollectionFilter(graph_editor_note_action_property.note_filter_groups,
                                                  PitchUtils.note_pitch_from_id(note_id),
                                                  keyframe_generator_property.note_property != "Pitch",
                                                  graph_editor_note_action_property.add_filters, context)
    return NoteCollection(notes, note_collection_meta_data, overlap_strategy, note_collection_filter)


class FcurveKeyframeGenerator:
    def __init__(self, operator, fcurve, min_keyframe_value: float, max_keyframe_value: float,
                 keyframe_generator_property):
        self.fcurve = fcurve
        self.min_keyframe_value = min_keyframe_value
        self.max_keyframe_value = max_keyframe_value
        self.keyframe_generator_property = keyframe_generator_property
        self.generate_at_note_end: bool = keyframe_generator_property.generate_at_note_end
        self.on_keyframe_overlap: str = keyframe_generator_property.on_keyframe_overlap
        self.operator = operator  # blender operator that can be used for report
        self.note_property: str = keyframe_generator_property.note_property

    def generate_keyframes_from_range_list(self, value_range_list, notes):
        """
        :param value_range_list: list of values to generate keyframes based on
        :param notes: list of notes
        :param value_from_note: function to get the value from the note
        """
        if len(value_range_list) == 0:
            return
        values_map = {}
        interval = (self.max_keyframe_value - self.min_keyframe_value) / len(value_range_list)
        mapped_keyframe_value = self.min_keyframe_value
        for value in value_range_list:
            values_map[value] = mapped_keyframe_value
            mapped_keyframe_value += interval

        keyframe_points = self.fcurve.keyframe_points
        existing_keyframes = existing_keyframe_map(keyframe_points)
        for note in notes:
            value = value_from_analyzed_note(self.note_property, note)
            if value in values_map:
                frame = note.note_end_frame if self.generate_at_note_end else note.note_start_frame
                add_keyframe(keyframe_points, existing_keyframes, frame, values_map[value], self.on_keyframe_overlap)

        # triggers Blender's re-calculation of keyframe control points.
        bpy.ops.transform.translate()

    def generate_keyframes_from_range(self, value_range_low, value_range_high, notes):
        """
        :param value_range_low: value from note that corresponds to min_keyframe_value
        :param value_range_high: value from note that corresponds to max_keyframe_value
        :param notes: list of notes
        """

        keyframe_points = self.fcurve.keyframe_points
        existing_keyframes = existing_keyframe_map(keyframe_points)
        if value_range_low != value_range_high:
            slope = (self.max_keyframe_value - self.min_keyframe_value) / (value_range_high - value_range_low)
        else:
            # map to min and map to max are the same, map both to min in this case
            # (can't map same value to two different numbers)
            slope = 0
        y_intercept = self.min_keyframe_value - slope * value_range_low
        for note in notes:
            value = value_from_analyzed_note(self.note_property, note)
            keyframe_value = slope * value + y_intercept
            frame = note.note_end_frame if self.generate_at_note_end else note.note_start_frame
            add_keyframe(keyframe_points, existing_keyframes, frame, keyframe_value, self.on_keyframe_overlap)

        # triggers Blender's re-calculation of keyframe control points.
        bpy.ops.transform.translate()


class GraphEditorMidiKeyframeGenerator(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    bl_idname = "ops.nla_midi_graph_editor_keyframe_generator"
    bl_label = "Generate Keyframes"
    bl_description = "Generate Keyframes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        loaded_midi_data = midi_data.get_midi_data(MidiDataType.GRAPH_EDITOR)

        graph_editor_note_action_property = loaded_midi_data \
            .selected_note_action_property(context)
        keyframe_generator_property = graph_editor_note_action_property.keyframe_generators[0]

        note_collection = get_note_collection(loaded_midi_data, context,
                                              graph_editor_note_action_property, keyframe_generator_property)

        min_keyframe_value = getattr(keyframe_generator_property,
                                     GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator_property.unit_type][
                                         3])
        max_keyframe_value = getattr(keyframe_generator_property,
                                     GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator_property.unit_type][
                                         4])
        analyzed_notes = note_collection.notes_on_first_layer() \
            if keyframe_generator_property.on_note_overlap == "skip" else note_collection.filtered_notes
        for fcurve in context.selected_editable_fcurves:
            self.generate_keyframes(fcurve, analyzed_notes, context, keyframe_generator_property, loaded_midi_data,
                                    max_keyframe_value, min_keyframe_value)

    def generate_keyframes(self, fcurve, analyzed_notes, context, keyframe_generator_property, loaded_midi_data,
                           max_keyframe_value, min_keyframe_value):
        keyframe_generator = FcurveKeyframeGenerator(self, fcurve,
                                                     min_keyframe_value, max_keyframe_value,
                                                     keyframe_generator_property)
        if keyframe_generator_property.note_property == "Pitch":
            pitch_list = self.pitch_range_list(keyframe_generator_property, {x[0] for x in loaded_midi_data.notes_list})
            keyframe_generator.generate_keyframes_from_range_list(pitch_list, analyzed_notes)
        else:
            keyframe_generator.generate_keyframes_from_range(
                getattr(keyframe_generator_property,
                        note_property_definitions[keyframe_generator_property.note_property][1]),
                getattr(keyframe_generator_property,
                        note_property_definitions[keyframe_generator_property.note_property][2]),
                analyzed_notes)

    @staticmethod
    def pitch_range_list(keyframe_generator_property, notes_in_active_track) -> List[int]:
        pitch_min = PitchUtils.note_pitch_from_id(keyframe_generator_property.pitch_min)
        pitch_max = PitchUtils.note_pitch_from_id(keyframe_generator_property.pitch_max)
        step = 1 if pitch_max >= pitch_min else -1
        return [pitch for pitch in range(pitch_min, pitch_max + step, step) if
                GraphEditorMidiKeyframeGenerator.passes_pitch_filter(pitch, keyframe_generator_property,
                                                                     notes_in_active_track)]

    @staticmethod
    def passes_pitch_filter(pitch: int, keyframe_generator_property, notes_in_active_track) -> bool:
        filter_by_scale = False
        in_scale = True
        if keyframe_generator_property.scale_filter_type == "In scale":
            filter_by_scale = True
        elif keyframe_generator_property.scale_filter_type == "Not in scale":
            filter_by_scale = True
            in_scale = False
        scale_pitch = None
        if filter_by_scale:
            scale_pitch = PitchUtils.SCALE_TO_PITCH_MAP[keyframe_generator_property.scale_filter_scale]
        passes_scale_filter = PitchUtils.note_in_scale(pitch, scale_pitch) == in_scale \
            if filter_by_scale else True

        filter_by_active_track = keyframe_generator_property.only_notes_in_selected_track
        note_id: str = PitchUtils.note_id_from_pitch(pitch)
        passes_track_filter = note_id in notes_in_active_track if filter_by_active_track else True

        return passes_scale_filter and passes_track_filter


class LoadMinMaxFromMidiTrack(bpy.types.Operator):
    bl_idname = "ops.nla_midi_load_min_max_from_midi_track"
    bl_label = "Load min and max values"
    bl_description = "Load minimum and maximum vales from the Midi Track"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        loaded_midi_data = midi_data.get_midi_data(MidiDataType.GRAPH_EDITOR)

        graph_editor_note_action_property = loaded_midi_data \
            .selected_note_action_property(context)
        keyframe_generator_property = graph_editor_note_action_property.keyframe_generators[0]

        note_collection = get_note_collection(loaded_midi_data, context,
                                              graph_editor_note_action_property, keyframe_generator_property)

        note_property = keyframe_generator_property.note_property
        note_property_values = [value_from_analyzed_note(note_property, analyzed_note) for analyzed_note in
                                note_collection.all_notes]
        if len(note_property_values) > 0:
            min_value = min(note_property_values)
            max_value = max(note_property_values)
            if note_property == "Pitch":
                min_note = PitchUtils.note_id_from_pitch(min_value)
                max_note = PitchUtils.note_id_from_pitch(max_value)
                setattr(keyframe_generator_property, note_property_definitions[note_property][1], min_note)
                setattr(keyframe_generator_property, note_property_definitions[note_property][2], max_note)
            else:
                setattr(keyframe_generator_property, note_property_definitions[note_property][1], min_value)
                setattr(keyframe_generator_property, note_property_definitions[note_property][2], max_value)
