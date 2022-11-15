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
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import PitchUtils
    from . import GraphEditorMidiPropertiesModule
    from . import NoteCollectionModule
    from . import OperatorUtils
    from .i18n import i18n

import bpy
from collections import defaultdict
from typing import List, Tuple, Optional
from .midi_data import MidiDataType
from .NoteCollectionModule import NoteCollection, NoteCollectionMetaData, NoteCollectionOverlapStrategy, \
    NoteCollectionFilter, AnalyzedNote


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
            return frame
    elif overlap_mode == 'PREVIOUS_FRAME':
        if not existing_keyframes[frame]:
            add(frame)
            return frame
        elif not existing_keyframes[frame - 1]:
            add(frame - 1)
            return frame - 1
    elif overlap_mode == 'NEXT_FRAME':
        if not existing_keyframes[frame]:
            add(frame)
            return frame
        elif not existing_keyframes[frame + 1]:
            add(frame + 1)
            return frame + 1
    else:  # replace
        add(frame)
        return frame
    return None


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
        self.keyframe_placement: str = keyframe_generator_property.keyframe_placement
        self.on_keyframe_overlap: str = keyframe_generator_property.on_keyframe_overlap
        self.operator = operator  # blender operator that can be used for report
        self.note_property: str = keyframe_generator_property.note_property
        self.limit_transition_length: bool = keyframe_generator_property.limit_transition_length
        self.transition_limit_frames: int = keyframe_generator_property.transition_limit_frames
        self.transition_offset_frames: int = keyframe_generator_property.transition_offset_frames
        self.transition_placement: str = keyframe_generator_property.transition_placement

    def add_transition_frames(self, keyframe_points,
                              transition_ranges: List[Tuple[Tuple[int, float], Tuple[int, float]]]):
        """
        :param keyframe_points: FCurveKeyframePoints
        :param transition_ranges: starting transition ranges and values (first and last keyframes)
        """

        def keyframe_exists_in_range(range_exclusive: Tuple[Tuple[int, float], Tuple[int, float]]):
            """
            :param range_exclusive: existing first and last keyframes
            :return: True if a keyframe exists between first and last (not including first and last)
            """
            for x in range(range_exclusive[0][0] + 1, range_exclusive[1][0]):
                if x in existing_keyframes:
                    return True
            return False

        if not self.limit_transition_length:
            return

        existing_keyframes = existing_keyframe_map(keyframe_points)
        for transition_range in transition_ranges:
            transition_frame_start = transition_range[0][0]
            transition_frame_end = transition_range[1][0]
            if (transition_frame_end - transition_frame_start) > self.transition_limit_frames and \
                    not keyframe_exists_in_range(transition_range):
                transition_frame_offset = min(
                    transition_range[1][0] - transition_range[0][0] - self.transition_limit_frames,
                    self.transition_offset_frames)
                if self.transition_placement == "end":
                    transition_frame_end = transition_frame_end - transition_frame_offset
                    transition_frame_start = transition_frame_end - self.transition_limit_frames
                else:
                    transition_frame_start = transition_frame_start + transition_frame_offset
                    transition_frame_end = transition_frame_start + self.transition_limit_frames
                add_keyframe(keyframe_points, existing_keyframes, transition_frame_start, transition_range[0][1],
                             "SKIP")
                add_keyframe(keyframe_points, existing_keyframes, transition_frame_end, transition_range[1][1], "SKIP")

        pass

    def add_keyframes(self, notes: List[AnalyzedNote], keyframe_points,
                      keyframe_value_from_note):
        def add_keyframes(generate_at_note_end: bool, on_keyframe_overlap: str) -> List[Tuple[int, int, float]]:
            """
            :param generate_at_note_end: if True generate at the end of the note, else generate at the start
            :param on_keyframe_overlap: behavior if existing keyframe on the same frame
            :return: list of (note index, frame, keyframe value)
            """
            existing_keyframes = existing_keyframe_map(keyframe_points)
            keyframe_data_added = []
            for i in range(len(notes)):
                note = notes[i]
                keyframe_value = keyframe_value_from_note(note)
                if keyframe_value is not None:
                    frame = note.note_end_frame if generate_at_note_end else note.note_start_frame
                    frame_added_to = add_keyframe(keyframe_points, existing_keyframes, frame, keyframe_value,
                                                  on_keyframe_overlap)
                    if frame_added_to is not None:
                        keyframe_data_added.append((i, frame_added_to, keyframe_value))
            return keyframe_data_added

        def create_transition_ranges(start_list: List[Tuple[int, int, float]],
                                     end_list: Optional[List[Tuple[int, int, float]]]) \
                -> List[Tuple[Tuple[int, float], Tuple[int, float]]]:
            """
            :param start_list: list of (note index, frame, keyframe value)
            :param end_list: optional list of (note index, frame, keyframe value)
            :return: list of ((transition start frame, transition start value),
            (transition end frame, transition end value)). Transitions between keyframes if only start_list is provided.
            If start_list and end_list are provided, transitions are from the end of the notes (based on end_list) to
            the start of the next note (based on start_list)
            """
            range_list = []
            if end_list is None:
                previous_frame_data = None
                for frame_data in start_list:
                    if previous_frame_data is not None and (previous_frame_data[0] + 1 == frame_data[0]):
                        range_list.append((previous_frame_data[1:], frame_data[1:]))
                    previous_frame_data = frame_data
            else:
                start_frame_data_index = 0
                for end_frame_data in end_list:
                    while start_frame_data_index < len(start_list) and start_list[start_frame_data_index][1] <= \
                            end_frame_data[1]:
                        start_frame_data_index += 1
                    if start_frame_data_index < len(start_list) and start_list[start_frame_data_index][0] == \
                            end_frame_data[0] + 1:
                        range_list.append((end_frame_data[1:], start_list[start_frame_data_index][1:]))
            return range_list

        if self.keyframe_placement == "note_start":
            self.add_transition_frames(keyframe_points,
                                       create_transition_ranges(add_keyframes(False, self.on_keyframe_overlap), None))
        elif self.keyframe_placement == "note_end":
            self.add_transition_frames(keyframe_points,
                                       create_transition_ranges(add_keyframes(True, self.on_keyframe_overlap), None))
        elif self.keyframe_placement == "note_start_and_end":
            self.add_transition_frames(keyframe_points,
                                       create_transition_ranges(add_keyframes(False, self.on_keyframe_overlap),
                                                                add_keyframes(True, "PREVIOUS_FRAME")))

    def generate_keyframes_from_range_list(self, value_range_list, notes):
        """
        :param value_range_list: list of values to generate keyframes based on
        :param notes: list of notes
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
        self.add_keyframes(notes, keyframe_points,
                           lambda note: values_map.get(value_from_analyzed_note(self.note_property, note), None))

        # triggers Blender's re-calculation of keyframe control points.
        bpy.ops.transform.translate()

    def generate_keyframes_from_range(self, value_range_low, value_range_high, notes):
        """
        :param value_range_low: value from note that corresponds to min_keyframe_value
        :param value_range_high: value from note that corresponds to max_keyframe_value
        :param notes: list of notes
        """

        keyframe_points = self.fcurve.keyframe_points
        if value_range_low != value_range_high:
            slope = (self.max_keyframe_value - self.min_keyframe_value) / (value_range_high - value_range_low)
        else:
            # map to min and map to max are the same, map both to min in this case
            # (can't map same value to two different numbers)
            slope = 0
        y_intercept = self.min_keyframe_value - slope * value_range_low
        self.add_keyframes(notes, keyframe_points,
                           lambda note: value_from_analyzed_note(self.note_property, note) * slope + y_intercept)

        # triggers Blender's re-calculation of keyframe control points.
        bpy.ops.transform.translate()


class GraphEditorMidiKeyframeGenerator(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    bl_idname = "ops.nla_midi_graph_editor_keyframe_generator"
    bl_label = i18n.get_key(i18n.GENERATE_KEYFRAMES_OP)
    bl_description = i18n.get_key(i18n.GENERATE_KEYFRAMES)
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
        if keyframe_generator_property.scale_filter_type == "in_scale":
            filter_by_scale = True
        elif keyframe_generator_property.scale_filter_type == "not_in_scale":
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
    bl_label = i18n.get_key(i18n.LOAD_MIN_AND_MAX_VALUES_OP)
    bl_description = i18n.get_key(i18n.LOAD_MIN_MAX_DESCRIPTION)
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
