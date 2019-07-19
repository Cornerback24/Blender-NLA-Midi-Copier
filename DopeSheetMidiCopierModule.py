if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    from . import midi_data

import bpy


class DopeSheetMidiCopier(bpy.types.Operator):
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
        dope_sheet_note_action_property = midi_data_property.dope_sheet_note_action_property
        frame_offset = (midi_data_property.midi_frame_start - 1) + dope_sheet_note_action_property.midi_frame_offset
        frames_per_second = context.scene.render.fps

        grease_pencils = [x.data for x in context.selected_objects if x.type == "GPENCIL"]

        for grease_pencil in grease_pencils:
            for layer in grease_pencil.layers:
                if not layer.lock:  # don't edit locked layers
                    DopeSheetMidiCopier.copy_gpencil_frames(layer, frame_offset, frames_per_second, context)

    @staticmethod
    def copy_gpencil_frames(g_pencil_layer, frame_offset, frames_per_second, context):
        """
        Copies frames on the g_pencil_layer based on the project's DopeSheetMidiPropertyGroup property
        :param g_pencil_layer: GPencilLayer object
        :param frame_offset: offset in frames from the start of the note to copy the first keyframe to
        :param frames_per_second: project frames per second
        :param context: blender context object
        :return: None
        """
        source_keyframes = [keyframe for keyframe in g_pencil_layer.frames if keyframe.select]
        if len(source_keyframes) == 0:
            return  # no keyframes to copy on this layer

        g_pencil_frames = g_pencil_layer.frames

        notes = midi_data.MidiDataUtil.get_notes(midi_data.dope_sheet_midi_data.get_track_id(context),
                                                 midi_data.dope_sheet_midi_data.get_note_id(context),
                                                 midi_data.dope_sheet_midi_data)

        if context.scene.dope_sheet_midi_data_property.dope_sheet_note_action_property.skip_overlaps:
            DopeSheetMidiCopier.copy_gpencil_frames_with_overlap_check(source_keyframes, g_pencil_frames, notes,
                                                                       frames_per_second, frame_offset)
        else:

            DopeSheetMidiCopier.copy_gpencil_frames_no_overlap_check(source_keyframes, g_pencil_frames, notes,
                                                                     frames_per_second, frame_offset)

        if context.scene.dope_sheet_midi_data_property.dope_sheet_note_action_property.delete_source_keyframes:
            for keyframe in source_keyframes:
                g_pencil_frames.remove(keyframe)

            # update the active_frame since the previous active_frame has been deleted
            g_pencil_layer.active_frame = g_pencil_layer.frames[0]

    @staticmethod
    def copy_gpencil_frames_no_overlap_check(source_keyframes, g_pencil_frames, notes, frames_per_second, frame_offset):
        """
        Copies the source_keyframes in the g_pencil_frames to every note in notes.

        :param source_keyframes: keyframes to copy
        :param g_pencil_frames: GPencilFrames object containing the keyframes
        :param notes: list of notes to copy frames to
        :param frames_per_second: project frames per second
        :param frame_offset: offset in frames from the start of the note to copy the first keyframe to
        :return: None
        """
        first_keyframe_frame_number = min([frame.frame_number for frame in source_keyframes])

        for note in notes:
            first_frame = (note.startTime / 1000) * frames_per_second + frame_offset
            for keyframe in source_keyframes:
                copied_frame = g_pencil_frames.copy(keyframe)
                copied_frame.frame_number = first_frame + (keyframe.frame_number - first_keyframe_frame_number)

    @staticmethod
    def copy_gpencil_frames_with_overlap_check(source_keyframes, g_pencil_frames, notes, frames_per_second,
                                               frame_offset):
        """
        Copies the source_keyframes in the g_pencil_frames to every note in notes, skipping any overlaps.

        :param source_keyframes: keyframes to copy
        :param g_pencil_frames: GPencilFrames object containing the keyframes
        :param notes: list of notes to copy frames to
        :param frames_per_second: project frames per second
        :param frame_offset: offset in frames from the start of the note to copy the first keyframe to
        :return: None
        """
        first_keyframe_frame_number = min([frame.frame_number for frame in source_keyframes])
        last_keyframe_frame_number = max([frame.frame_number for frame in source_keyframes])
        action_length = last_keyframe_frame_number - first_keyframe_frame_number
        last_frame = -1 - action_length  # initialize to frame before any actions will be copied to

        for note in notes:
            first_frame = (note.startTime / 1000) * frames_per_second + frame_offset
            # check for overlap
            if first_frame - last_frame > 0:
                last_frame = first_frame + action_length
                for keyframe in source_keyframes:
                    copied_frame = g_pencil_frames.copy(keyframe)
                    copied_frame.frame_number = first_frame + (keyframe.frame_number - first_keyframe_frame_number)
