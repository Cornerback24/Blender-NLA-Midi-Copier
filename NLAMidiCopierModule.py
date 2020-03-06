if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
else:
    from . import midi_data
    from . import PitchUtils
    from . import NoteFilterImplementations

import bpy
from .midi_analysis.Note import Note


class NoteActionCopier:

    def __init__(self, note_action_property, context):
        midi_data_property = context.scene.midi_data_property
        self.context = context
        self.frame_offset = midi_data_property.midi_frame_start + note_action_property.midi_frame_offset
        self.frames_per_second = context.scene.render.fps
        self.context = context
        self.duplicate_on_overlap = note_action_property.id_type == "Object" and \
                                    note_action_property.duplicate_object_on_overlap
        self.scale_to_note_length = note_action_property.sync_length_with_notes
        self.scale_factor = note_action_property.scale_factor
        self.action = note_action_property.action
        self.filter_groups_property = note_action_property.note_filter_groups
        self.add_filters = note_action_property.add_filters
        # actual length of the action
        self.true_action_length = None if self.action is None else \
            self.action.frame_range[1] - self.action.frame_range[0]
        # action length as set by the note action property
        self.action_length = None if self.action is None else \
            max(self.true_action_length, note_action_property.action_length)
        self.note_action_track_name = note_action_property.nla_track_name

        self.id_type = note_action_property.id_type
        animated_object_property = midi_data.ID_PROPERTIES_DICTIONARY[self.id_type][0]
        self.animated_object = getattr(note_action_property, animated_object_property)

    def copy_notes_to_object_with_duplication(self, track_name, notes):
        if not notes:
            return  # no notes to copy, do nothing

        nla_track = self.create_nla_track(self.animated_object, track_name)
        # list of [nla_track, [(frame, scale_factor)], last_frame]
        actions_to_copy = []

        first_note = notes[0]
        first_frame = self.first_frame(first_note)
        non_scaled_length = self.note_action_length(notes[0])

        copied_action_length, scale_factor = self.copied_action_length_and_scale_factor(notes[0], non_scaled_length)
        last_frame = first_frame + copied_action_length
        actions_to_copy.append([nla_track, [(first_frame, scale_factor)], last_frame])

        for note in notes[1:]:
            first_frame = self.first_frame(note)
            copied_action_length, scale_factor = self.copied_action_length_and_scale_factor(notes[0], non_scaled_length)
            last_frame = first_frame + copied_action_length
            # track_info is [nla_track, [frames], last_frame]
            track_info = next((x for x in actions_to_copy if first_frame > x[2]), None)
            if track_info is None:
                # create a duplicated objected for overlapping actions
                duplicated_object = NoteActionCopier.duplicated_object(self.animated_object, self.context)
                # the original object should already have a track for the actions, look for the duplicated track
                duplicated_nla_track = None
                if duplicated_object.animation_data is not None:
                    # find an empty track with a name matching track_name
                    duplicated_nla_track = next((x for x in duplicated_object.animation_data.nla_tracks if
                                                 x.name == track_name and len(x.strips) == 0), None)
                # create a new track if the duplicated track wasn't found
                if duplicated_nla_track is None:
                    duplicated_nla_track = self.create_nla_track(duplicated_object, track_name)

                actions_to_copy.append(
                    [duplicated_nla_track, [(first_frame, scale_factor)], last_frame])
            else:
                track_info[1].append((first_frame, scale_factor)),
                track_info[2] = last_frame

        for x in actions_to_copy:
            nla_track = x[0]
            for frame_and_scale_factor in x[1]:
                NoteActionCopier.copy_action(frame_and_scale_factor[0], self.action, nla_track,
                                             frame_and_scale_factor[1])

    def copy_notes_to_object_no_duplication(self, track_name, notes):
        if not notes:
            return  # no notes to copy, do nothing

        nla_track = self.create_nla_track(self.animated_object, track_name)
        non_scaled_length = self.note_action_length(notes[0])

        # initialize to frame before any actions will be copied to
        last_frame = -1 - self.copied_action_length_and_scale_factor(notes[0], non_scaled_length)[0]

        for note in notes:
            first_frame = self.first_frame(note)
            # check for action overlap
            if first_frame - last_frame > 0:
                copied_action_length, scale_factor = self.copied_action_length_and_scale_factor(note, non_scaled_length)
                last_frame = first_frame + copied_action_length
                NoteActionCopier.copy_action(first_frame, self.action, nla_track, scale_factor)

    def copied_action_length_and_scale_factor(self, note, non_scaled_length):
        if self.scale_to_note_length:
            copied_action_length = self.note_action_length(note)
            return copied_action_length, self.note_scale_factor(copied_action_length)
        else:
            return non_scaled_length, 1

    def note_action_length(self, note):
        """
        :param note: Note object
        :return: length of the action to sync with the note, in frames
        """
        return self.note_length_frames(note) * self.scale_factor \
            if self.scale_to_note_length else self.action_length

    def note_scale_factor(self, copied_action_length):
        """
        :param copied_action_length: length of the action after being copied
        :return: the scale factor to apply to the original action to set its length to copied_action_length
        """
        return copied_action_length / self.true_action_length

    def note_length_frames(self, note):
        """
        :param note: Note object
        :return: length of the Note in frames
        """
        return midi_data.MidiDataUtil.note_length_frames(note, self.frames_per_second) \
            if self.scale_to_note_length else self.action_length

    def copy_notes_to_object(self, track_id, note_id: str):
        if self.action is None or self.animated_object is None:
            return
        track_name = self.note_action_track_name
        if track_name is None or len(track_name) == 0:
            track_name = note_id + " - " + track_id
        notes = midi_data.MidiDataUtil.get_notes(track_id, midi_data.midi_data)
        notes = NoteFilterImplementations.filter_notes(notes, self.filter_groups_property,
                                                       PitchUtils.note_pitch_from_id(note_id),
                                                       self.add_filters, self.context)

        if self.duplicate_on_overlap:
            self.copy_notes_to_object_with_duplication(track_name, notes)
        else:
            self.copy_notes_to_object_no_duplication(track_name, notes)

    def copy_notes_to_objects(self, track_id: str, note_id: str, objects):
        for x in objects:
            self.animated_object = x
            self.copy_notes_to_object(track_id, note_id)

    def first_frame(self, note):
        """
        :param note: Note object
        :return: the first frame for an action syncing up to this note
        """
        return (note.startTime / 1000) * self.frames_per_second + self.frame_offset

    @staticmethod
    def duplicated_object(original_object, context):
        # this method assumes no objects are selected when called
        # neither the original object nor the duplicated object will be selected when this method returns
        original_object.select_set(True)
        bpy.ops.object.duplicate()
        duplicated_object = context.selected_objects[0]
        duplicated_object.select_set(False)
        original_object.select_set(False)
        return duplicated_object

    def create_nla_track(self, animated_object, track_name):
        if self.action.id_root == "NODETREE":
            animation_data = NoteActionCopier.get_animation_data(animated_object.node_tree)
        else:
            animation_data = NoteActionCopier.get_animation_data(animated_object)
        nla_track = animation_data.nla_tracks.new()
        nla_track.name = track_name
        return nla_track

    @staticmethod
    def get_animation_data(animated_object):
        animation_data = animated_object.animation_data
        # ensure object has animation data
        if animation_data is None:
            animation_data = animated_object.animation_data_create()
        return animation_data

    @staticmethod
    def copy_action(frame, action, nla_track, scale_factor):
        nla_strips = nla_track.strips
        copied_strip = nla_strips.new(str(frame) + ' ' + action.name, frame, action)
        copied_strip.scale = scale_factor


class NLAMidiCopier(bpy.types.Operator):
    bl_idname = "ops.nla_midi_copier"
    bl_label = "Copy Action to Notes"
    bl_description = "Copy the selected Action to the selected note"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        note_action_property = midi_data.midi_data.selected_note_action_property(context)

        id_type = note_action_property.id_type

        selected_objects = bpy.context.selected_objects if id_type == "OBJECT" else []
        for x in selected_objects:
            x.select_set(False)
        note_action_copier = NoteActionCopier(note_action_property, context)

        if note_action_copier.animated_object is not None:
            note_action_copier.copy_notes_to_object(midi_data.get_track_id(context), midi_data.get_note_id(context))
        elif id_type == "Object" and note_action_property.copy_to_selected_objects:
            selected_objects = bpy.context.selected_objects

            note_action_copier.copy_notes_to_objects(midi_data.get_track_id(context),
                                                     midi_data.get_note_id(context), selected_objects)

        # preserve state of which objects were selected
        for x in selected_objects:
            x.select_set(True)


class NLAMidiInstrumentCopier(bpy.types.Operator):
    bl_idname = "ops.nla_midi_instrument_copier"
    bl_label = "Animate Instrument"
    bl_description = "Animate Instrument"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        instrument = midi_data.selected_instrument(context)
        self.animate_instrument(context, instrument)

    @staticmethod
    def animate_instrument(context, instrument):
        track_id = instrument.selected_midi_track
        for instrument_note in instrument.notes:
            pitch = instrument_note.note_id
            for note_action in instrument_note.actions:
                NoteActionCopier(note_action, context).copy_notes_to_object(track_id,
                                                                            PitchUtils.note_id_from_pitch(pitch))


class NLAMidiAllInstrumentCopier(bpy.types.Operator):
    bl_idname = "ops.nla_midi_all_instrument_copier"
    bl_label = "Animate All Instruments"
    bl_description = "Animate All Instruments"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        for instrument in context.scene.midi_data_property.instruments:
            NLAMidiInstrumentCopier.animate_instrument(context, instrument)
