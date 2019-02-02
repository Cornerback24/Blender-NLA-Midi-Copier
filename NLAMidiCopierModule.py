if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
else:
    from . import midi_data
import bpy


class NLAMidiCopier(bpy.types.Operator):
    bl_idname = "ops.nla_midi_copier"
    bl_label = "Copy Action to Notes"
    bl_description = "Copy the selected NLA-Strip(s) to the selected note"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    def action_common(self, context):
        midi_data_property = context.scene.midi_data_property
        note_action_property = midi_data_property.note_action_property
        self.frames_per_second = context.scene.render.fps
        self.frame_offset = (midi_data_property.midi_frame_start - 1) + note_action_property.midi_frame_offset

        id_type = note_action_property.id_type
        animated_object_property = midi_data.ID_PROPERTIES_DICTIONARY[id_type][0]
        animated_object = getattr(note_action_property, animated_object_property)
        notes = midi_data.get_selected_notes(context)
        selected_objects = bpy.context.selected_objects if id_type == "OBJECT" else []
        for x in selected_objects:
            x.select_set(False)
        if animated_object is not None:
            self.copy_notes_to_object(animated_object, note_action_property, notes, context)
        elif id_type == "Object" and note_action_property.copy_to_selected_objects:
            selected_objects = bpy.context.selected_objects
            for x in selected_objects:
                self.copy_notes_to_object(x, note_action_property, notes, context)

        # preserve state of which objects were selected
        for x in selected_objects:
            x.select_set(True)

    def copy_notes_to_object(self, animated_object, note_action_property, notes, context):
        duplicate_on_overlap = note_action_property.id_type == "Object" and \
                               note_action_property.duplicate_object_on_overlap
        action = note_action_property.action

        track_name = note_action_property.nla_track_name
        if track_name is None or len(track_name) == 0:
            track_name = midi_data.get_note_id(context) + " - " + midi_data.get_track_id(context)
        nla_track = NLAMidiCopier.create_nla_track(animated_object, track_name)

        action_length = max(action.frame_range[1] - action.frame_range[0], note_action_property.action_length)
        # change to note_action_property.action_length reflect actual action length if it was shorter
        note_action_property.action_length = action_length
        last_frame = -1 - action_length  # initialize to frame before any actions will be copied to

        if duplicate_on_overlap:
            # list of [nla_track, [frames], last_frame]
            actions_to_copy = []

            first_note = next(iter(notes), None)
            if first_note is not None:
                first_frame = self.first_frame(first_note)
                last_frame = first_frame + action_length
                actions_to_copy.append([nla_track, [first_frame], last_frame])

            for note in notes[1:]:
                first_frame = self.first_frame(note)
                last_frame = first_frame + action_length
                # track_info is [nla_track, [frames], last_frame]
                track_info = next((x for x in actions_to_copy if first_frame > x[2]), None)
                if track_info is None:
                    # create a duplicated objected for overlapping actions
                    duplicated_object = NLAMidiCopier.duplicated_object(animated_object, context)
                    # the original object should already have a track for the actions, look for the duplicated track
                    duplicated_nla_track = None
                    if duplicated_object.animation_data is not None:
                        # find an empty track with a name matching track_name
                        duplicated_nla_track = next((x for x in duplicated_object.animation_data.nla_tracks if
                                                     x.name == track_name and len(x.strips) == 0), None)
                    # create a new track if the duplicated track wasn't found
                    if duplicated_nla_track is None:
                        duplicated_nla_track = NLAMidiCopier.create_nla_track(duplicated_object, track_name)

                    actions_to_copy.append([duplicated_nla_track, [first_frame], last_frame])
                else:
                    track_info[1].append(first_frame),
                    track_info[2] = last_frame

            for x in actions_to_copy:
                nla_track = x[0]
                for frame in x[1]:
                    NLAMidiCopier.copy_action(frame, action, nla_track)
        else:
            for note in notes:
                first_frame = self.first_frame(note)
                # check for action overlap
                if first_frame - last_frame > 0:
                    last_frame = first_frame + action_length
                    NLAMidiCopier.copy_action(first_frame, action, nla_track)

    def first_frame(self, note):
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

    @staticmethod
    def create_nla_track(animated_object, track_name):
        animation_data = NLAMidiCopier.get_animation_data(animated_object)
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
    def copy_action(frame, action, nla_track):
        nla_strips = nla_track.strips
        nla_strips.new(str(frame) + ' ' + action.name, frame, action)
