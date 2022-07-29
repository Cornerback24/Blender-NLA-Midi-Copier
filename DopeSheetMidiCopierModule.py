if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteCollectionModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OperatorUtils)
else:
    from . import midi_data
    from . import NoteFilterImplementations
    from . import PitchUtils
    from . import NoteCollectionModule
    from . import OperatorUtils

import bpy
from .midi_data import MidiDataType
from .NoteCollectionModule import NoteCollection, NoteCollectionMetaData, NoteCollectionOverlapStrategy, \
    NoteCollectionFilter


class DopeSheetMidiCopier(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    bl_idname = "ops.nla_midi_dope_sheet_copier"
    bl_label = "Copy Keyframes to Notes"
    bl_description = "Copy the selected keyframes to the selected note"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        DopeSheetMidiCopier.copy_keyframes(context, context.scene.dope_sheet_midi_data_property)

    @staticmethod
    def copy_keyframes(context, midi_data_property):
        """
        Copies GPencil Frames to notes based on the project's DopeSheetMidiPropertyGroup property

        :param context: blender context object
        :param midi_data_property: DopeSheetMidiPropertyGroup
        :return:
        """
        dope_sheet_note_action_property = midi_data_property.note_action_property
        frame_offset = midi_data_property.midi_frame_start + dope_sheet_note_action_property.midi_frame_offset
        frames_per_second = context.scene.render.fps
        copy_to_note_end = dope_sheet_note_action_property.copy_to_note_end

        grease_pencils = [x.data for x in context.selected_objects if x.type == "GPENCIL"]

        for grease_pencil in grease_pencils:
            for layer in grease_pencil.layers:
                if not layer.lock:  # don't edit locked layers
                    DopeSheetMidiCopier.copy_gpencil_frames(layer, frame_offset, frames_per_second, copy_to_note_end,
                                                            context)

    @staticmethod
    def copy_gpencil_frames(g_pencil_layer, frame_offset: int, frames_per_second: float, copy_to_note_end: bool,
                            context):
        """
        Copies frames on the g_pencil_layer based on the project's DopeSheetMidiPropertyGroup property
        :param g_pencil_layer: GPencilLayer object
        :param frame_offset: offset in frames from the start of the note to copy the first keyframe to
        :param frames_per_second: project frames per second
        :param copy_to_note_end: copy to the end of the note
        :param context: blender context object
        :return: None
        """
        source_keyframes = [keyframe for keyframe in g_pencil_layer.frames if keyframe.select]
        if len(source_keyframes) == 0:
            return  # no keyframes to copy on this layer
        g_pencil_frames = g_pencil_layer.frames
        first_keyframe_frame_number = min([frame.frame_number for frame in source_keyframes])
        last_keyframe_frame_number = max([frame.frame_number for frame in source_keyframes])
        non_scaled_action_length = max(last_keyframe_frame_number - first_keyframe_frame_number, 1)

        loaded_midi_data = midi_data.get_midi_data(MidiDataType.DOPESHEET)
        dope_sheet_note_action_property = context.scene.dope_sheet_midi_data_property.note_action_property
        notes = midi_data.MidiDataUtil.get_notes(loaded_midi_data.get_track_id(context),
                                                 loaded_midi_data)
        note_id = loaded_midi_data.get_note_id(context)

        overlap_strategy = NoteCollectionOverlapStrategy(False, False, True)
        note_collection_filter = NoteCollectionFilter(dope_sheet_note_action_property.note_filter_groups,
                                                      PitchUtils.note_pitch_from_id(note_id), True,
                                                      dope_sheet_note_action_property.add_filters, context)
        note_collection_meta_data = NoteCollectionMetaData.from_note_action_property(
            loaded_midi_data, context, dope_sheet_note_action_property, non_scaled_action_length)
        note_collection = NoteCollection(notes, note_collection_meta_data, overlap_strategy, note_collection_filter)

        analyzed_notes = note_collection.notes_on_first_layer() \
            if dope_sheet_note_action_property.skip_overlaps else note_collection.filtered_notes
        for analyzed_note in analyzed_notes:
            for keyframe in source_keyframes:
                copied_frame = g_pencil_frames.copy(keyframe)
                copied_frame.frame_number = (analyzed_note.action_length_frames * (
                        keyframe.frame_number - first_keyframe_frame_number)) // analyzed_note.non_scaled_action_length \
                                            + analyzed_note.action_start_frame

        if context.scene.dope_sheet_midi_data_property.note_action_property.delete_source_keyframes:
            for keyframe in source_keyframes:
                g_pencil_frames.remove(keyframe)
