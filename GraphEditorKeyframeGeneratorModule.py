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
    importlib.reload(CCDataModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OperatorUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(i18n)
else:
    from . import midi_data
    from . import PitchUtils
    from . import GraphEditorMidiPropertiesModule
    from . import NoteCollectionModule
    from . import CCDataModule
    from . import OperatorUtils
    from .i18n import i18n

import bpy
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any
from .midi_data import MidiDataType
from .NoteCollectionModule import NoteCollection, NoteCollectionMetaData, NoteCollectionOverlapStrategy, \
    NoteCollectionFilter


class KeyframeData:
    def __init__(self, keyframe_points):
        self.keyframe_points = keyframe_points
        # map frame number to list of keyframes
        self.frames_to_keyframes: Dict[int, List[Any]] = defaultdict(list)
        for keyframe in keyframe_points:
            self.frames_to_keyframes[keyframe.co[0]].append(keyframe)
        self.frames_existing_before_additions = {x.co[0] for x in self.keyframe_points}

    def keyframe_existed_before_additions(self, frame: int) -> bool:
        return frame in self.frames_existing_before_additions

    def keyframe_exists(self, frame: int) -> bool:
        return frame in self.frames_to_keyframes

    def add_keyframe(self, frame_number: int, keyframe_value: float):
        if frame_number in self.frames_to_keyframes:
            del self.frames_to_keyframes[frame_number]
        added_keyframe = self.keyframe_points.insert(frame_number, keyframe_value, options={'REPLACE'})
        self.frames_to_keyframes[frame_number].append(added_keyframe)


def add_keyframe(keyframe_data: KeyframeData, frame: int, keyframe_value: float, overlap_mode: str) -> Optional[int]:
    """
    :param keyframe_data: keyframe data
    :param frame: frame
    :param keyframe_value: keyframe value
    :param overlap_mode: overlap mode enum string
    """

    if overlap_mode == 'SKIP':
        if not keyframe_data.keyframe_existed_before_additions(frame):
            keyframe_data.add_keyframe(frame, keyframe_value)
            return frame
    elif overlap_mode == 'PREVIOUS_FRAME':
        if not keyframe_data.keyframe_existed_before_additions(frame):
            keyframe_data.add_keyframe(frame, keyframe_value)
            return frame
        elif not keyframe_data.keyframe_exists(frame - 1):
            keyframe_data.add_keyframe(frame - 1, keyframe_value)
            return frame - 1
    elif overlap_mode == 'NEXT_FRAME':
        if not keyframe_data.keyframe_existed_before_additions(frame):
            keyframe_data.add_keyframe(frame, keyframe_value)
            return frame
        elif not keyframe_data.keyframe_exists(frame + 1):
            keyframe_data.add_keyframe(frame + 1, keyframe_value)
            return frame + 1
    else:  # replace
        keyframe_data.add_keyframe(frame, keyframe_value)
        return frame


note_property_definitions = {"Pitch": (lambda analyzed_note: analyzed_note.note.pitch, "pitch_min", "pitch_max"),
                             "Length": (lambda analyzed_note: analyzed_note.note_length_frames, "non_negative_min",
                                        "non_negative_max"),
                             "Velocity": (lambda analyzed_note: analyzed_note.note.velocity, "int_0_to_127_min",
                                          "int_0_to_127_max")}


def value_from_analyzed_note(note_property: str, analyzed_note):
    return note_property_definitions[note_property][0](analyzed_note)


def get_note_collection(loaded_midi_data, context, graph_editor_note_action_property, keyframe_generator_property):
    graph_editor_midi_data_property = context.scene.graph_editor_midi_data_property
    notes = midi_data.MidiDataUtil.get_notes(loaded_midi_data.get_track_id(context), loaded_midi_data)
    note_collection_meta_data = NoteCollectionMetaData(loaded_midi_data, context.scene.render.fps,
                                                       graph_editor_midi_data_property.midi_frame_start +
                                                       graph_editor_note_action_property.midi_frame_offset,
                                                       False, None, None)
    overlap_strategy = NoteCollectionOverlapStrategy(False, False, False)
    note_id = loaded_midi_data.get_note_id(context)
    note_collection_filter = NoteCollectionFilter(graph_editor_note_action_property.note_filter_groups,
                                                  PitchUtils.note_pitch_from_id(note_id),
                                                  keyframe_generator_property.note_property != "Pitch",
                                                  graph_editor_note_action_property.add_filters, context)
    return NoteCollection(notes, note_collection_meta_data, overlap_strategy, note_collection_filter)


def get_cc_data(loaded_midi_data, context):
    return midi_data.MidiDataUtil.get_cc_data(
        loaded_midi_data.get_track_id(context), loaded_midi_data, context,
        context.scene.graph_editor_midi_data_property.note_action_property.midi_frame_offset)


class FcurveKeyframeGenerator:
    def __init__(self, operator, fcurve, min_keyframe_value: float, max_keyframe_value: float,
                 keyframe_generator_property):
        self.fcurve = fcurve
        self.keyframe_data = KeyframeData(fcurve.keyframe_points)
        self.min_keyframe_value = min_keyframe_value
        self.max_keyframe_value = max_keyframe_value
        self.keyframe_generator_property = keyframe_generator_property
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
                if transition_keyframe_data.keyframe_exists(x):
                    return True
            return False

        if not self.limit_transition_length:
            return

        transition_keyframe_data = KeyframeData(keyframe_points)
        for transition_range in transition_ranges:
            transition_frame_start = transition_range[0][0]
            transition_frame_end = transition_range[1][0]
            if (transition_frame_end - transition_frame_start) > self.transition_limit_frames and not \
                    keyframe_exists_in_range(transition_range):
                transition_frame_offset = min(
                    transition_range[1][0] - transition_range[0][0] - self.transition_limit_frames,
                    self.transition_offset_frames)
                if self.transition_placement == "end":
                    transition_frame_end = transition_frame_end - transition_frame_offset
                    transition_frame_start = transition_frame_end - self.transition_limit_frames
                else:
                    transition_frame_start = transition_frame_start + transition_frame_offset
                    transition_frame_end = transition_frame_start + self.transition_limit_frames
                add_keyframe(transition_keyframe_data, transition_frame_start, transition_range[0][1], "SKIP")
                add_keyframe(transition_keyframe_data, transition_frame_end, transition_range[1][1], "SKIP")

    def add_keyframes(self, frame_keyframe_value_pairs, on_keyframe_overlap_override: Optional[str] = None) \
            -> List[Tuple[int, float]]:
        """
        :param frame_keyframe_value_pairs: list of (frame, keyframe value)
        :param on_keyframe_overlap_override: overrides the property if provided
        :return: list of (frame, keyframe value)
        """
        keyframe_data_added = {}
        for frame_keyframe_value_pair in frame_keyframe_value_pairs:
            keyframe_value = frame_keyframe_value_pair[1]
            if keyframe_value is not None:
                frame = frame_keyframe_value_pair[0]
                frame_added_to = add_keyframe(
                    self.keyframe_data, frame, keyframe_value,
                    on_keyframe_overlap_override if on_keyframe_overlap_override is not None else
                    self.on_keyframe_overlap)
                if frame_added_to is not None:
                    keyframe_data_added[frame_added_to] = (frame_added_to, keyframe_value)

        return list(keyframe_data_added.values())

    @staticmethod
    def create_transition_ranges(end_list: List[Tuple[int, float]],
                                 start_list: Optional[List[Tuple[int, float]]]) -> List[
        Tuple[Tuple[int, float], Tuple[int, float]]]:
        """
        :param start_list: list of (frame, keyframe value) for the start of a transition
        :param end_list: optional list of (frame, keyframe value) for the end of a transition
        :return: list of ((transition start frame, transition start value),
        (transition end frame, transition end value)).
        Transitions from start frame to end frame where there are no other frames between.
        Transitions between keyframes if start_list and end_list are the same or start_list is None.
        """
        # list of (frame, value, start_or_end) where start_or_end is 0 for end, 1 for start
        if start_list is None:
            start_list = end_list
        combined_list = sorted([(x[0], x[1], 0) for x in end_list] + [(x[0], x[1], 1) for x in start_list],
                               key=lambda x: (x[0], x[2]))
        range_list = []
        for i in range(len(combined_list) - 1):
            start_frame = combined_list[i]
            end_frame = combined_list[i + 1]
            # no transition between end and start frames
            if end_frame[0] > start_frame[0] and not (start_frame[2] == 0 and end_frame[2] == 1):
                range_list.append(((start_frame[0], start_frame[1]), (end_frame[0], end_frame[1])))
        return range_list

    def generate_keyframes_from_range_list(self, value_range_list, frame_value_pairs,
                                           on_keyframe_overlap_override: Optional[str] = None):
        """
        Generates keyframes based on a list of values. Keyframe values are equidistant between each source value in
        value_range_list
        :param value_range_list: list of values to generate keyframes based on
        :param frame_value_pairs: List of (frame, value). value must be in value_range_list for keyframes to be
        generated
        :param on_keyframe_overlap_override: overrides the property if provided
        :return: list of (frame, keyframe value)
        """
        if len(value_range_list) == 0:
            return []
        values_map = {}
        interval = 0 if len(value_range_list) < 2 else (self.max_keyframe_value - self.min_keyframe_value) / (
                len(value_range_list) - 1)
        mapped_keyframe_value = self.min_keyframe_value
        for value in value_range_list:
            values_map[value] = mapped_keyframe_value
            mapped_keyframe_value += interval

        frame_keyframe_value_pairs = ((x[0], values_map.get(x[1])) for x in frame_value_pairs if x[1] in values_map)
        return self.add_keyframes(frame_keyframe_value_pairs, on_keyframe_overlap_override)

    def generate_keyframes_from_range(self, value_range_low, value_range_high, frame_value_pairs,
                                      on_keyframe_overlap_override: Optional[str] = None):
        """
        :param value_range_low: value from note that corresponds to min_keyframe_value
        :param value_range_high: value from note that corresponds to max_keyframe_value
        :param frame_value_pairs: list of (frame, value)
        :param on_keyframe_overlap_override: overrides the property if provided
        :return: list of (frame, keyframe value)
        """

        if value_range_low != value_range_high:
            slope = (self.max_keyframe_value - self.min_keyframe_value) / (value_range_high - value_range_low)
        else:
            # map to min and map to max are the same, map both to min in this case
            # (can't map same value to two different numbers)
            slope = 0
        y_intercept = self.min_keyframe_value - slope * value_range_low
        frame_keyframe_value_pairs = ((x[0], x[1] * slope + y_intercept) for x in frame_value_pairs)
        return self.add_keyframes(frame_keyframe_value_pairs, on_keyframe_overlap_override)


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

        graph_editor_note_action_property = loaded_midi_data.selected_note_action_property(context)
        keyframe_generator_property = graph_editor_note_action_property.keyframe_generators[0]

        note_collection = get_note_collection(loaded_midi_data, context, graph_editor_note_action_property,
                                              keyframe_generator_property)

        min_keyframe_value = getattr(keyframe_generator_property,
                                     GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator_property.unit_type][
                                         3])
        max_keyframe_value = getattr(keyframe_generator_property,
                                     GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator_property.unit_type][
                                         4])
        analyzed_notes = note_collection.notes_on_first_layer() if keyframe_generator_property.on_note_overlap == \
                                                                   "skip" else note_collection.filtered_notes
        for fcurve in context.selected_editable_fcurves:
            self.generate_keyframes(fcurve, analyzed_notes, keyframe_generator_property, loaded_midi_data,
                                    max_keyframe_value, min_keyframe_value, context)

    def generate_keyframes(self, fcurve, analyzed_notes, keyframe_generator_property,
                           loaded_midi_data, max_keyframe_value, min_keyframe_value, context):
        keyframe_generator = FcurveKeyframeGenerator(self, fcurve, min_keyframe_value, max_keyframe_value,
                                                     keyframe_generator_property)
        if keyframe_generator_property.property_type == "cc_data":
            self.generate_keyframes_from_cc_data(fcurve, analyzed_notes, keyframe_generator,
                                                 keyframe_generator_property, loaded_midi_data, context)
        else:
            self.generate_keyframes_from_note_data(fcurve, analyzed_notes, keyframe_generator,
                                                   keyframe_generator_property, loaded_midi_data)

        # triggers Blender's re-calculation of keyframe control points
        bpy.ops.transform.translate()

    def generate_keyframes_from_note_data(self, fcurve, analyzed_notes, keyframe_generator,
                                          keyframe_generator_property, loaded_midi_data):
        def build_frame_value_list(frame_from_analyzed_note) -> List[Tuple[int, float]]:
            return [(frame_from_analyzed_note(analyzed_note),
                     value_from_analyzed_note(note_property, analyzed_note))
                    for analyzed_note in analyzed_notes]

        def map_to_min():
            return getattr(keyframe_generator_property,
                           note_property_definitions[keyframe_generator_property.note_property][1])

        def map_to_max():
            return getattr(keyframe_generator_property,
                           note_property_definitions[keyframe_generator_property.note_property][2])

        note_end_keyframes = None
        note_start_keyframes = None
        note_property = keyframe_generator_property.note_property
        on_note_start = keyframe_generator_property.keyframe_placement_note_start
        on_note_end = keyframe_generator_property.keyframe_placement_note_end
        if note_property == "Pitch":
            pitch_list = self.pitch_range_list(keyframe_generator_property, {x[0] for x in loaded_midi_data.notes_list})
            if on_note_start:
                frame_value_list = build_frame_value_list(lambda analyzed_note: analyzed_note.note_start_frame)
                note_start_keyframes = keyframe_generator.generate_keyframes_from_range_list(pitch_list,
                                                                                             frame_value_list)
            if on_note_end:
                frame_value_list = build_frame_value_list(lambda analyzed_note: analyzed_note.note_end_frame)
                note_end_keyframes = keyframe_generator.generate_keyframes_from_range_list(
                    pitch_list, frame_value_list, "PREVIOUS_FRAME" if on_note_start else None)
        else:
            if on_note_start:
                frame_value_list = build_frame_value_list(lambda analyzed_note: analyzed_note.note_start_frame)
                note_start_keyframes = keyframe_generator.generate_keyframes_from_range(
                    map_to_min(), map_to_max(), frame_value_list)
            if on_note_end:
                frame_value_list = build_frame_value_list(lambda analyzed_note: analyzed_note.note_end_frame)
                note_end_keyframes = keyframe_generator.generate_keyframes_from_range(
                    map_to_min(), map_to_max(), frame_value_list, "PREVIOUS_FRAME" if on_note_start else None)

        if note_end_keyframes is not None and note_start_keyframes is not None:
            keyframe_generator.add_transition_frames(
                fcurve.keyframe_points,
                keyframe_generator.create_transition_ranges(note_start_keyframes, note_end_keyframes))
        elif note_start_keyframes is not None:
            keyframe_generator.add_transition_frames(
                fcurve.keyframe_points, keyframe_generator.create_transition_ranges(note_start_keyframes, None))
        elif note_end_keyframes is not None:
            keyframe_generator.add_transition_frames(
                fcurve.keyframe_points, keyframe_generator.create_transition_ranges(note_end_keyframes, None))

    def generate_keyframes_from_cc_data(self, fcurve, analyzed_notes, keyframe_generator,
                                        keyframe_generator_property, loaded_midi_data, context):

        def add_keyframes(frame_list, on_keyframe_overlap_override: Optional[str] = None):
            frame_value_list = [(frame, cc_controller_data.value_at_frame(frame)) for frame in frame_list]
            return keyframe_generator.generate_keyframes_from_range(
                map_to_min(), map_to_max(), frame_value_list, on_keyframe_overlap_override)

        def map_to_min():
            return keyframe_generator_property.int_0_to_127_min

        def map_to_max():
            return keyframe_generator_property.int_0_to_127_max

        if not keyframe_generator_property.cc_type:
            return  # no cc type selected
        cc_controller_data = get_cc_data(loaded_midi_data, context).get_cc_controller_data(
            int(keyframe_generator_property.cc_type))
        if cc_controller_data is None:
            return

        on_note_start = keyframe_generator_property.keyframe_placement_note_start
        on_note_end = keyframe_generator_property.keyframe_placement_note_end
        on_cc_data_change = keyframe_generator_property.keyframe_placement_cc_data_change
        added_keyframes = []
        if on_note_start:
            added_keyframes += add_keyframes([analyzed_note.note_start_frame for analyzed_note in analyzed_notes])
        if on_note_end:
            added_keyframes += add_keyframes([analyzed_note.note_end_frame for analyzed_note in analyzed_notes],
                                             "PREVIOUS_FRAME" if on_note_start else None)
        if on_cc_data_change:
            added_keyframes += add_keyframes(
                [cc_event_data.time_frames for cc_event_data in cc_controller_data.cc_event_data])

        keyframe_generator.add_transition_frames(fcurve.keyframe_points,
                                                 keyframe_generator.create_transition_ranges(added_keyframes, None))

    @staticmethod
    def pitch_range_list(keyframe_generator_property, notes_in_active_track) -> List[int]:
        """
        :param keyframe_generator_property: keyframe generator property
        :param notes_in_active_track: list of note id strings of notes in active track
        :return: list of pitches to use in keyframe value calculation
        """
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
        passes_scale_filter = PitchUtils.note_in_scale(pitch, scale_pitch) == in_scale if filter_by_scale else True

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

        graph_editor_note_action_property = loaded_midi_data.selected_note_action_property(context)
        keyframe_generator_property = graph_editor_note_action_property.keyframe_generators[0]

        if keyframe_generator_property.property_type == "cc_data":
            self.load_min_max_cc_data(keyframe_generator_property, loaded_midi_data, context)
        else:
            self.load_min_max_note_property(context, graph_editor_note_action_property, keyframe_generator_property,
                                            loaded_midi_data)

    def load_min_max_note_property(self, context, graph_editor_note_action_property, keyframe_generator_property,
                                   loaded_midi_data):
        note_collection = get_note_collection(loaded_midi_data, context, graph_editor_note_action_property,
                                              keyframe_generator_property)
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

    def load_min_max_cc_data(self, keyframe_generator_property, loaded_midi_data, context):
        if not keyframe_generator_property.cc_type:
            return  # no cc type selected
        cc_controller_data = get_cc_data(loaded_midi_data, context).get_cc_controller_data(
            int(keyframe_generator_property.cc_type))
        if cc_controller_data is not None:
            min_max_pair = cc_controller_data.min_max()
            if min_max_pair is not None:
                keyframe_generator_property.int_0_to_127_min = min_max_pair[0]
                keyframe_generator_property.int_0_to_127_max = min_max_pair[1]
