from . import midi_data
from . import PitchUtils
from . import OperatorUtils
from .i18n import i18n
from bpy.app import version as blender_version

import bpy
from .midi_data import MidiDataType
from .NoteCollectionModule import NoteCollection, NoteCollectionMetaData, NoteCollectionOverlapStrategy, \
    NoteCollectionFilter


class NLA_MIDI_COPIER_PT_dope_sheet_copier(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    bl_idname = "nla_midi_copier.dope_sheet_copier"
    bl_label = i18n.get_key(i18n.COPY_KEYFRAMES_TO_NOTES_OP)
    bl_description = i18n.get_key(i18n.COPY_KEYFRAMES_TO_NOTES_DESCRIPTION)
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        NLA_MIDI_COPIER_PT_dope_sheet_copier.copy_keyframes(context,
                                                            context.scene.nla_midi_copier_main_property_group.dope_sheet_midi_data_property)

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

        grease_pencil_type = "GREASEPENCIL" if blender_version >= (4, 3, 0) else "GPENCIL"
        grease_pencils = [x.data for x in context.selected_objects if x.type == grease_pencil_type]

        for grease_pencil in grease_pencils:
            for layer in grease_pencil.layers:
                if not layer.lock:  # don't edit locked layers
                    NLA_MIDI_COPIER_PT_dope_sheet_copier.copy_gpencil_frames(layer, frame_offset, frames_per_second,
                                                                             copy_to_note_end,
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
        dope_sheet_note_action_property = (
            context.scene.nla_midi_copier_main_property_group.dope_sheet_midi_data_property.note_action_property)
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

        source_keyframe_frame_numbers = [keyframe.frame_number for keyframe in source_keyframes]
        existing_frame_numbers = {keyframe.frame_number for keyframe in g_pencil_layer.frames}
        for analyzed_note in analyzed_notes:
            if blender_version >= (4, 3, 0):
                for source_frame_number in source_keyframe_frame_numbers:
                    copy_to_frame_number = int((analyzed_note.action_length_frames * (
                            source_frame_number - first_keyframe_frame_number)) //
                                               analyzed_note.non_scaled_action_length
                                               + analyzed_note.action_start_frame)
                    if copy_to_frame_number not in existing_frame_numbers:
                        existing_frame_numbers.add(copy_to_frame_number)
                        g_pencil_frames.copy(source_frame_number, copy_to_frame_number)
            else:
                for keyframe in source_keyframes:
                    copied_frame = g_pencil_frames.copy(keyframe)
                    copied_frame.frame_number = int((analyzed_note.action_length_frames * (
                            keyframe.frame_number - first_keyframe_frame_number)) //
                                                    analyzed_note.non_scaled_action_length
                                                    + analyzed_note.action_start_frame)

        if (context.scene.nla_midi_copier_main_property_group.dope_sheet_midi_data_property.note_action_property
                .delete_source_keyframes):
            for keyframe in source_keyframes:
                g_pencil_frames.remove(keyframe)
