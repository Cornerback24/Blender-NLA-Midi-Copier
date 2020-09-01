if "bpy" in locals():
    import importlib

    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(midi_data)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PitchUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(ObjectUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(PropertyUtils)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteFilterImplementations)
else:
    from . import midi_data
    from . import PitchUtils
    from . import ObjectUtils
    from . import PropertyUtils
    from . import NoteFilterImplementations

import bpy
from typing import List, Tuple, Optional
from .midi_analysis.Note import Note


class ActionToCopy:
    def __init__(self, action, nla_track, first_frame: int, last_frame: int, scale_factor: float, blend_type: str,
                 strips_to_shift):
        self.action = action
        self.nla_track = nla_track
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.scale_factor = scale_factor
        self.blend_type = blend_type
        self.strips_to_shift = strips_to_shift

    def copy_action(self):
        # shift strips to the right if adding the non-scaled action will caused an overlap
        shift_amount_frames = 0
        if len(self.strips_to_shift) > 0:
            true_action_length = self.action.frame_range[1] - self.action.frame_range[0]
            shift_amount_frames = self.first_frame + true_action_length - self.strips_to_shift[0].frame_start + 1
            for strip in reversed(self.strips_to_shift):
                strip.frame_end = strip.frame_end + shift_amount_frames
                strip.frame_start = strip.frame_start + shift_amount_frames

        nla_strips = self.nla_track.strips
        copied_strip = nla_strips.new(str(self.first_frame) + ' ' + self.action.name, self.first_frame, self.action)
        copied_strip.frame_end = self.last_frame
        if self.blend_type is not None:
            copied_strip.blend_type = self.blend_type
            copied_strip.extrapolation = "NOTHING"

        # moved shifted strips back
        if shift_amount_frames > 0:
            for strip in self.strips_to_shift:
                strip.frame_start = strip.frame_start - shift_amount_frames
                strip.frame_end = strip.frame_end - shift_amount_frames


class NlaTrackInfo:
    def __init__(self, nla_track, blend_type: Optional[str]):
        self.blend_type = blend_type
        self.nla_track = nla_track
        self.current_nla_strip_index = 0
        self.nla_strips = nla_track.strips
        self.nla_strip_count = len(nla_track.strips)
        self.last_action_added: Optional[ActionToCopy] = None

    def existing_action_overlap(self, first_frame: int, last_frame: int):
        """
        :param first_frame: the first frame of the action
        :param last_frame:  the last frame of the action
        :return: True if the action overlaps an action that exists on the track
        (does not include actions that will be copied). This method needs to be called in ascending order by first frame
        of actions being checked (does not check for actions that are known to be before the last action that was
        checked in order to be more efficient).
        """
        while self.current_nla_strip_index < self.nla_strip_count and \
                self.nla_strips[self.current_nla_strip_index].frame_start < last_frame:
            if self.nla_strips[self.current_nla_strip_index].frame_end > first_frame:
                return True
            self.current_nla_strip_index = self.current_nla_strip_index + 1
        return False

    def overlaps_last_added_action(self, action_first_frame: int, action_last_frame: int) -> bool:
        """
        :param action_first_frame: the first frame of the action
        :param action_last_frame: the last frame of the action
        :return: True if the action overlaps the most recent action that was added to be copied
        """
        if self.last_action_added is None:
            overlaps_last_action = False
        else:
            overlaps_last_action = action_first_frame < self.last_action_added.last_frame and action_last_frame > \
                                   self.last_action_added.first_frame
        return overlaps_last_action

    def actions_to_shift_when_copy(self, action_last_frame: int):
        """
        :param action_last_frame: copied actions's last frame
        :return: list of actions that would need to be shifted to the right in order to make room for the copied action
        """
        if self.current_nla_strip_index >= self.nla_strip_count:
            return []
        else:
            if self.nla_strips[self.current_nla_strip_index].frame_start <= action_last_frame:
                return self.nla_strips[self.current_nla_strip_index:]
            else:
                return []

    def has_room_for_action(self, action_first_frame: int, action_last_frame: int) -> bool:
        return not self.existing_action_overlap(action_first_frame, action_last_frame) \
               and not self.overlaps_last_added_action(action_first_frame, action_last_frame)

    def add_action(self, action, first_frame: int, last_frame: int, scale_factor: float,
                   actions_to_shift) -> ActionToCopy:
        self.last_action_added = ActionToCopy(action, self.nla_track, first_frame, last_frame, scale_factor,
                                              self.blend_type, actions_to_shift)
        return self.last_action_added


class NlaTracksManager:
    def __init__(self, action, track_name: str, animated_object, context, duplicate_on_overlap: bool, blend_mode: str):
        self.action = action
        self.track_name: str = track_name
        self.animated_object = animated_object
        self.context = context
        self.duplicate_on_overlap: bool = duplicate_on_overlap
        self.blend_mode: str = blend_mode

        self.nla_track_infos: List[NlaTrackInfo] = []
        self.track_overlap_index: int = 0
        self.skip_overlaps: bool = blend_mode == "None"
        self.original_track: [NlaTrackInfo] = self.next_track()
        self.objects_using_data = None
        self.true_action_length = self.action.frame_range[1] - self.action.frame_range[0]
        pass

    def action_to_copy(self, first_frame: int, last_frame: int, action_scale_factor: float) -> Optional[ActionToCopy]:
        nla_track_info = self.track_for_action(first_frame, last_frame)
        if nla_track_info is not None:
            # If the action is scaled down, there may be a conflict when adding the action at first since it will not
            # be caused down at that point and could extend past the next strip. In this case, temporarily shift
            # actions to the right to make space.
            actions_to_shift = nla_track_info.actions_to_shift_when_copy(
                first_frame + self.true_action_length) if action_scale_factor < 1 else []
            return nla_track_info.add_action(self.action, first_frame, last_frame, action_scale_factor,
                                             actions_to_shift)
        return None

    def track_for_action(self, first_frame: int, last_frame: int) -> Optional[NlaTrackInfo]:
        if self.duplicate_on_overlap:
            # if the original track doesn't have room, don't duplicate the object
            # (duplicated object would not have room either)
            if self.original_track.existing_action_overlap(first_frame, last_frame):
                return None
            else:
                nla_track_info = next((track_info for track_info in self.nla_track_infos if
                                       track_info.has_room_for_action(first_frame, last_frame)), None)
                return nla_track_info if nla_track_info is not None else self.next_track()
        else:
            if self.skip_overlaps:
                return self.original_track if self.original_track.has_room_for_action(first_frame, last_frame) else None
            else:
                # Start from the top nla track and search down. Don't place a strip on a track below a track that
                # doesn't have room (drop the strip on top of the stack).
                nla_track_info = None
                room_for_strip = True
                track_index = len(self.nla_track_infos) - 1
                while room_for_strip and track_index >= 0:
                    track_info = self.nla_track_infos[track_index]
                    track_index = track_index - 1
                    if track_info.has_room_for_action(first_frame, last_frame):
                        nla_track_info = track_info
                    else:
                        room_for_strip = False

                if nla_track_info is None:
                    # Create a new track or find the next existing track matching the name with space for the action
                    nla_track_info = self.next_track()
                    while not nla_track_info.has_room_for_action(first_frame, last_frame):
                        nla_track_info = self.next_track()
                return nla_track_info

    def next_track(self) -> Optional[NlaTrackInfo]:
        nla_tracks_empty = len(self.nla_track_infos) == 0
        if self.duplicate_on_overlap and not nla_tracks_empty:
            duplicated_object = self.duplicated_object()
            if duplicated_object is None:
                return None
            # the original object should already have a track for the actions, look for the duplicated track
            duplicated_nla_track = None
            if duplicated_object.animation_data is not None:
                # find a track with a name matching track_name
                duplicated_nla_track = next((x for x in duplicated_object.animation_data.nla_tracks if
                                             x.name == self.track_name), None)
            # create a new track if the duplicated track wasn't found
            if duplicated_nla_track is None:
                duplicated_nla_track = self.get_or_create_nla_track(duplicated_object, self.track_name)
            nla_track_info = NlaTrackInfo(duplicated_nla_track, None)
        else:
            new_track_name = self.track_name if nla_tracks_empty else f"{self.track_name} {len(self.nla_track_infos) + 1}"
            blend_type = None if nla_tracks_empty else \
                (None if self.blend_mode is None or self.blend_mode == "None" else self.blend_mode)
            nla_track_info = NlaTrackInfo(self.get_or_create_nla_track(self.animated_object, new_track_name),
                                          blend_type)

        self.nla_track_infos.append(nla_track_info)

        return nla_track_info

    def get_or_create_nla_track(self, animated_object, track_name: str):
        if self.action.id_root == "NODETREE":
            animation_data = NoteActionCopier.get_animation_data(animated_object.node_tree)
        else:
            animation_data = NoteActionCopier.get_animation_data(animated_object)
        for track in animation_data.nla_tracks:
            if track.name == track_name:
                return track
        nla_track = animation_data.nla_tracks.new()
        nla_track.name = track_name
        return nla_track

    def duplicated_object(self):
        # this method assumes no objects are selected when called
        # neither the original object nor the duplicated object will be selected when this method returns
        if self.action.id_root == "OBJECT":
            return NlaTracksManager.duplicate_object(self.animated_object, self.context)
        else:
            if self.objects_using_data is None:
                object_type = self.action.id_root
                self.objects_using_data = [x for x in self.context.blend_data.objects if
                                           x.type == object_type and x.data == self.animated_object]
            if len(self.objects_using_data) == 0:
                return None  # no objects to duplicate

            duplicated_object = NlaTracksManager.duplicate_object(self.objects_using_data[0], self.context)
            # create linked duplicates for any other objects using the data
            for x in self.objects_using_data[1:]:
                duplicate = NlaTracksManager.duplicate_object(x, self.context)
                duplicate.data = duplicated_object.data
            return duplicated_object.data

    @staticmethod
    def duplicate_object(object_to_duplicate, context):
        object_to_duplicate.select_set(True)
        bpy.ops.object.duplicate()
        duplicated_object = context.selected_objects[0]
        duplicated_object.select_set(False)
        object_to_duplicate.select_set(False)
        return duplicated_object


class NoteActionCopier:

    def __init__(self, note_action_property, context, instrument_track_name: Optional[str], additional_frame_offset=0):
        midi_data_property = context.scene.midi_data_property
        self.context = context
        self.frame_offset = midi_data_property.midi_frame_start + note_action_property.midi_frame_offset + \
                            additional_frame_offset
        self.frames_per_second = context.scene.render.fps
        self.context = context
        self.duplicate_on_overlap = midi_data.can_resolve_data_from_selected_objects(note_action_property.id_type) and \
                                    note_action_property.duplicate_object_on_overlap
        self.scale_to_note_length = note_action_property.sync_length_with_notes
        self.scale_factor = note_action_property.scale_factor
        self.copy_to_note_end = note_action_property.copy_to_note_end
        self.action = note_action_property.action
        self.filter_groups_property = note_action_property.note_filter_groups
        self.add_filters = note_action_property.add_filters
        # actual length of the action
        self.true_action_length = None if self.action is None else \
            self.action.frame_range[1] - self.action.frame_range[0]
        # action length as set by the note action property
        self.action_length = None if self.action is None else \
            max(self.true_action_length, note_action_property.action_length)
        self.blend_mode: str = note_action_property.blend_mode
        self.note_action_track_name: str = note_action_property.nla_track_name
        self.instrument_track_name = instrument_track_name

        self.id_type = note_action_property.id_type
        animated_object_property = midi_data.ID_PROPERTIES_DICTIONARY[self.id_type][0]
        self.animated_object = getattr(note_action_property, animated_object_property)

    def copy_notes(self, notes: List[Note], track_name: str):
        if not notes:
            return  # no notes to copy, do nothing

        non_scaled_length: float = self.note_action_length(notes[0])
        nla_tracks = NlaTracksManager(action=self.action,
                                      track_name=track_name,
                                      animated_object=self.animated_object,
                                      context=self.context,
                                      duplicate_on_overlap=self.duplicate_on_overlap,
                                      blend_mode=self.blend_mode)
        actions_to_copy = []
        for note in notes:
            action_length, action_scale_factor = self.copied_action_length_and_scale_factor(note, non_scaled_length)
            first_frame = self.first_frame(note)
            to_copy = nla_tracks.action_to_copy(first_frame, round(first_frame + action_length), action_scale_factor)
            if to_copy is not None:
                actions_to_copy.append(to_copy)
        for action_to_copy in actions_to_copy:
            action_to_copy.copy_action()

    def copied_action_length_and_scale_factor(self, note: Note, non_scaled_length: float) -> Tuple[float, float]:
        if self.scale_to_note_length:
            copied_action_length = self.note_action_length(note)
            return copied_action_length, self.note_scale_factor(copied_action_length)
        else:
            return non_scaled_length, 1

    def note_action_length(self, note) -> float:
        """
        :param note: Note object
        :return: Length of the action to sync with the note, in frames. Includes extra length beyond the action for
        user-defined object duplication action length.
        """
        return self.note_length_frames(note) * self.scale_factor \
            if self.scale_to_note_length else (
            self.action_length if self.duplicate_on_overlap else self.true_action_length)

    def note_scale_factor(self, copied_action_length) -> float:
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
            track_name = self.instrument_track_name if self.instrument_track_name else \
                note_id + " - " + track_id
        notes = midi_data.MidiDataUtil.get_notes(track_id, midi_data.midi_data)
        notes = NoteFilterImplementations.filter_notes(notes, self.filter_groups_property,
                                                       PitchUtils.note_pitch_from_id(note_id),
                                                       self.add_filters, self.context)

        self.copy_notes(notes, track_name)

    def copy_notes_to_objects(self, track_id: str, note_id: str, objects):
        for x in objects:
            self.animated_object = x
            self.copy_notes_to_object(track_id, note_id)

    def first_frame(self, note) -> int:
        """
        :param note: Note object
        :return: the first frame for an action syncing up to this note
        """
        return int(((note.endTime if self.copy_to_note_end else note.startTime) / 1000) \
               * self.frames_per_second + self.frame_offset)

    @staticmethod
    def get_animation_data(animated_object):
        animation_data = animated_object.animation_data
        # ensure object has animation data
        if animation_data is None:
            animation_data = animated_object.animation_data_create()
        return animation_data

    @staticmethod
    def get_selected_nla_strips_and_deselect(context):
        selected_strips = [strip for strip in context.selected_nla_strips]
        for strip in selected_strips:
            strip.select = False
        return selected_strips

    @staticmethod
    def select_nla_strips(nla_strips_to_select):
        for strip in nla_strips_to_select:
            strip.select = True


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

        selected_objects = context.selected_objects if midi_data.can_resolve_data_from_selected_objects(id_type) else []
        for x in selected_objects:
            x.select_set(False)
        note_action_copier = NoteActionCopier(note_action_property, context, None)

        if note_action_property.copy_to_selected_objects and midi_data.can_resolve_data_from_selected_objects(id_type):
            if midi_data.ID_PROPERTIES_DICTIONARY[id_type][1] == "OBJECT":
                objects_to_copy = selected_objects
            else:
                object_type = midi_data.ID_PROPERTIES_DICTIONARY[id_type][1]
                # multiple objects may use the same data so use a set to eliminate duplicates
                objects_to_copy = {x.data for x in selected_objects if x.type == object_type}

            note_action_copier.copy_notes_to_objects(midi_data.get_track_id(context),
                                                     midi_data.get_note_id(context), objects_to_copy)
        elif note_action_copier.animated_object is not None:
            note_action_copier.copy_notes_to_object(midi_data.get_track_id(context), midi_data.get_note_id(context))

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
        if instrument.copy_to_single_track:
            instrument_track_name = instrument.nla_track_name
            if not instrument_track_name:
                instrument_track_name = instrument.selected_midi_track
        else:
            instrument_track_name = None
        instrument_frame_offset = instrument.instrument_midi_frame_offset
        for instrument_note in instrument.notes:
            pitch = instrument_note.note_id
            for note_action in instrument_note.actions:
                NoteActionCopier(note_action, context, instrument_track_name, instrument_frame_offset) \
                    .copy_notes_to_object(track_id, PitchUtils.note_id_from_pitch(pitch))


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


class NLABulkMidiCopier(bpy.types.Operator):
    """
    This operator handles both copying to an instrument and copying to notes from the bulk copy panel.
    """
    bl_idname = "ops.nla_bulk_midi_copier"
    bl_label = "Copy Action to Notes"
    bl_description = "Copy the selected Action to the selected note"
    bl_options = {"REGISTER", "UNDO"}
    scale_to_pitch_map = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10,
                          "B": 11}
    in_major_scale = {0, 2, 4, 5, 7, 9, 11}  # pitches in a major scale (where 0 is tonic)
    tooltip: bpy.props.StringProperty()

    def execute(self, context):
        self.action_common(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.action_common(context)
        return {'FINISHED'}

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def action_common(self, context):
        copy_along_path: bool = context.scene.midi_data_property.bulk_copy_property.copy_along_path
        if copy_along_path:
            NLABulkMidiCopier.notes_along_path(context)
        else:
            NLABulkMidiCopier.single_note(context)

    @staticmethod
    def single_note(context):
        midi_panel_note_action_property = context.scene.midi_data_property.note_action_property
        bulk_copy_property = context.scene.midi_data_property.bulk_copy_property
        note_pitch: int = int(context.scene.midi_data_property.copy_to_instrument_selected_note_id)
        NLABulkMidiCopier.animate_or_copy_to_instrument(bulk_copy_property.copy_to_instrument,
                                                        PitchUtils.note_id_from_pitch(note_pitch),
                                                        midi_panel_note_action_property, context)

    @staticmethod
    def notes_along_path(context):
        """
        Copies the action to objects along the path, incrementing the note for each object.
        """
        bulk_copy_property = context.scene.midi_data_property.bulk_copy_property
        objs = ObjectUtils.objects_sorted_by_path(context.selected_objects,
                                                  bulk_copy_property.bulk_copy_curve)
        midi_data_property = midi_data.midi_data.get_midi_data_property(context)
        note_action_property = midi_data_property.note_action_property
        action_id_root = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][1]
        note_action_object_field = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][0]

        original_object_value = getattr(note_action_property, note_action_object_field)
        if action_id_root == "OBJECT":
            animated_objects = objs
        else:
            animated_objects = list(dict.fromkeys([x.data for x in objs if x.type == action_id_root]))

        notes_to_copy = NLABulkMidiCopier.notes_to_copy(midi_data_property.bulk_copy_property, midi_data.midi_data)

        for i in range(min(len(notes_to_copy), len(animated_objects))):
            animated_object = animated_objects[i]
            note_to_copy = notes_to_copy[i]
            setattr(note_action_property, note_action_object_field, animated_object)
            NLABulkMidiCopier.animate_or_copy_to_instrument(bulk_copy_property.copy_to_instrument, note_to_copy,
                                                            note_action_property, context)

        setattr(note_action_property, note_action_object_field, original_object_value)

    @staticmethod
    def notes_to_copy(bulk_copy_property, loaded_midi_data) -> List[str]:
        notes_to_copy_list = []
        note_pitch: int = int(bulk_copy_property.bulk_copy_starting_note)

        filter_by_active_track = bulk_copy_property.only_notes_in_selected_track
        filter_by_scale = False
        in_scale = True
        if bulk_copy_property.scale_filter_type == "In scale":
            filter_by_scale = True
        elif bulk_copy_property.scale_filter_type == "Not in scale":
            filter_by_scale = True
            in_scale = False

        notes_in_active_track = {}
        if filter_by_active_track:
            notes_in_active_track = {x[0] for x in loaded_midi_data.notes_list}
        scale_pitch = None
        if filter_by_scale:
            scale_pitch = NLABulkMidiCopier.scale_to_pitch_map[bulk_copy_property.scale_filter_scale]

        while note_pitch <= 127:
            note_id: str = PitchUtils.note_id_from_pitch(note_pitch)
            passes_scale_filter = (((note_pitch - scale_pitch) % 12) in NLABulkMidiCopier.in_major_scale) == in_scale \
                if filter_by_scale else True
            passes_track_filter = note_id in notes_in_active_track if filter_by_active_track else True
            if passes_scale_filter and passes_track_filter:
                notes_to_copy_list.append(note_id)
            note_pitch = note_pitch + 1

        return notes_to_copy_list

    @staticmethod
    def animate_or_copy_to_instrument(copy_to_instrument: bool, note_id: str, note_action_property, context):
        """
        :param copy_to_instrument: If true, copies the note action property to the instrument defined by
        midi_data.midi_data.selected_instrument_for_copy_to_id, otherwise copies the action using the given note
        :param note_id: note to copy to
        :param note_action_property: the note action property
        :param context: the context
        """
        if copy_to_instrument:
            instrument = midi_data.midi_data.selected_instrument_for_copy_to_id(context)
            if instrument is None:
                return
            copied_note_action_property = PropertyUtils.get_note_action_property(instrument,
                                                                                 PitchUtils.note_pitch_from_id(note_id))
            midi_panel_note_action_property = context.scene.midi_data_property.note_action_property
            PropertyUtils.copy_note_action_property(midi_panel_note_action_property, copied_note_action_property,
                                                    midi_data.ID_PROPERTIES_DICTIONARY)
        else:
            NoteActionCopier(note_action_property, context, None) \
                .copy_notes_to_object(midi_data.get_track_id(context), note_id)
