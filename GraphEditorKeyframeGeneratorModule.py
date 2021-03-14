if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(GraphEditorMidiPropertiesModule)
else:
    from . import midi_data
    from . import PitchUtils
    from . import GraphEditorMidiPropertiesModule

import bpy
from collections import defaultdict
from typing import List
from .midi_data import MidiDataType
from .NoteCollectionModule import NoteCollection


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


def generate_keyframes(fcurve, value_range_list, notes, value_from_note, min_keyframe_value: float,
                       max_keyframe_value: float, generate_at_note_end: bool, overlap_mode):
    if len(value_range_list) == 0:
        return
    values_map = {}
    interval = (max_keyframe_value - min_keyframe_value) / len(value_range_list)
    mapped_keyframe_value = min_keyframe_value
    for value in value_range_list:
        values_map[value] = mapped_keyframe_value
        mapped_keyframe_value += interval

    keyframe_points = fcurve.keyframe_points
    existing_keyframes = existing_keyframe_map(keyframe_points)
    for note in notes:
        value = value_from_note(note)
        if value in values_map:
            frame = note.end_frame if generate_at_note_end else note.start_frame
            add_keyframe(keyframe_points, existing_keyframes, frame, values_map[value], overlap_mode)

    # triggers Blender's re-calculation of keyframe control points.
    bpy.ops.transform.translate()


class GraphEditorMidiKeyframeGenerator(bpy.types.Operator):
    bl_idname = "ops.nla_midi_graph_editor_keyframe_generator"
    bl_label = "Generate Keyframes"
    bl_description = "Generate Keyframes"
    bl_options = {"REGISTER", "UNDO"}
    tooltip: bpy.props.StringProperty(options={'HIDDEN'})

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip if properties.tooltip else cls.bl_description

    def action_common(self, context):
        loaded_midi_data = midi_data.get_midi_data(MidiDataType.GRAPH_EDITOR)
        notes = midi_data.MidiDataUtil.get_notes(
            loaded_midi_data.get_track_id(context),
            loaded_midi_data)

        graph_editor_midi_data_property = context.scene.graph_editor_midi_data_property
        graph_editor_note_action_property = loaded_midi_data \
            .selected_note_action_property(context)
        keyframe_generator_property = graph_editor_note_action_property.keyframe_generators[0]

        note_collection = NoteCollection(
            notes, loaded_midi_data, context.scene.render.fps,
            graph_editor_midi_data_property.midi_frame_start + graph_editor_note_action_property.midi_frame_offset,
            False, None, None)

        min_keyframe_value = getattr(keyframe_generator_property,
                                     GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator_property.unit_type][
                                         3])
        max_keyframe_value = getattr(keyframe_generator_property,
                                     GraphEditorMidiPropertiesModule.UNIT_TYPES[keyframe_generator_property.unit_type][
                                         4])
        pitch_list = self.pitch_range_list(keyframe_generator_property, {x[0] for x in loaded_midi_data.notes_list})
        generate_keyframes(context.active_editable_fcurve, pitch_list,
                           note_collection.all_notes, lambda analyzed_note: analyzed_note.note.pitch,
                           min_keyframe_value, max_keyframe_value, keyframe_generator_property.generate_at_note_end,
                           keyframe_generator_property.on_keyframe_overlap)

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
