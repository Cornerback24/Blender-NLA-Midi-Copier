from collections import defaultdict

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
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(NoteCollectionModule)
    # noinspection PyUnresolvedReferences,PyUnboundLocalVariable
    importlib.reload(OperatorUtils)
else:
    from . import midi_data
    from . import PitchUtils
    from . import ObjectUtils
    from . import PropertyUtils
    from . import NoteFilterImplementations
    from . import NoteCollectionModule
    from . import OperatorUtils

import bpy
import re
from typing import List, Tuple, Optional, Any
from .midi_analysis.Note import Note
from .midi_data import MidiDataType
from .NoteCollectionModule import NoteCollectionOverlapStrategy, NoteCollectionMetaData, NoteCollection, \
    ExistingNoteOverlaps, NoteCollectionFilter


class ActionToCopy:
    def __init__(self, action, nla_track, first_frame: int, last_frame: int, blend_type: str, strips_to_shift):
        self.action = action
        self.nla_track = nla_track
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.blend_type = blend_type
        self.strips_to_shift = strips_to_shift

    def copy_action(self):
        # shift strips to the right if adding the non-scaled action will caused an overlap
        shift_amount_frames = 0
        if len(self.strips_to_shift) > 0:
            true_action_length = self.action.frame_range[1] - self.action.frame_range[0]
            shift_amount_frames = true_action_length
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
        self.nla_strips = nla_track.strips

    def actions_to_shift_when_copy(self, action_first_frame: int):
        """
        :param action_first_frame: copied action's first frame
        :return: list of actions that would need to be shifted to the right in order to make room for the copied action
        """
        index = 0
        nla_strip_count = len(self.nla_track.strips)
        while index < nla_strip_count:
            if self.nla_strips[index].frame_start > action_first_frame:
                return self.nla_strips[index:]
            index += 1
        return []

    def create_action_to_copy(self, action, first_frame: int, last_frame: int, actions_to_shift) -> ActionToCopy:
        return ActionToCopy(action, self.nla_track, first_frame, last_frame, self.blend_type, actions_to_shift)


class NlaTracksManager:
    def __init__(self, action, track_name: str, animated_object, context, duplicate_on_overlap: bool, blend_mode: str,
                 skip_overlaps: bool):
        self.action = action
        self.track_name: str = track_name
        self.animated_object = animated_object
        self.context = context
        self.duplicate_on_overlap: bool = duplicate_on_overlap
        self.blend_mode: str = blend_mode

        self.nla_track_infos: List[NlaTrackInfo] = []
        self.skip_overlaps: bool = skip_overlaps
        self.objects_using_data = None
        pass

    def copy_notes_to_tracks(self, note_collection: NoteCollection):
        nla_layer_track_paris = []
        if not self.duplicate_on_overlap and self.skip_overlaps:
            # skip overlaps so only the first layer
            for notes_layer in note_collection.notes_layers[:1]:
                nla_layer_track_paris.append((notes_layer, self.next_track()))
        else:
            for notes_layer in note_collection.notes_layers:
                # in the duplicate on overlap case, need to create new tracks before actions are placed on the original
                # so that new actions are not duplicated
                nla_layer_track_paris.append((notes_layer, self.next_track()))
        actions_to_copy_lists = []
        for notes_layer, nla_track_info in nla_layer_track_paris:
            actions_to_copy = []
            for analyzed_note in notes_layer.notes:
                action_to_copy = self.action_to_copy(analyzed_note.action_start_frame, analyzed_note.action_end_frame,
                                                     analyzed_note.is_scaled_down(), nla_track_info)
                if action_to_copy is not None:
                    actions_to_copy.append(action_to_copy)
            actions_to_copy_lists.append(actions_to_copy)
        for actions_to_copy in actions_to_copy_lists:
            for action_to_copy in actions_to_copy:
                action_to_copy.copy_action()

    def action_to_copy(self, first_frame: int, last_frame: int, scaled_down: bool, nla_track_info: NlaTrackInfo) \
            -> Optional[ActionToCopy]:
        if nla_track_info is not None:
            # If the action is scaled down, there may be a conflict when adding the action at first since it will not
            # be scaled down at that point and could extend past the next strip. In this case, temporarily shift
            # actions to the right to make space.
            actions_to_shift = nla_track_info.actions_to_shift_when_copy(first_frame) if scaled_down else []
            return nla_track_info.create_action_to_copy(self.action, first_frame, last_frame, actions_to_shift)
        return None

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
            new_track_name = self.get_track_name(len(self.nla_track_infos) + 1)
            blend_type = None if nla_tracks_empty else self.blend_mode  # no blending on first track
            nla_track_info = NlaTrackInfo(self.get_or_create_nla_track(self.animated_object, new_track_name),
                                          blend_type)

        self.nla_track_infos.append(nla_track_info)

        return nla_track_info

    def existing_tracks_list(self):
        name_plus_number_regex = re.compile(re.escape(self.track_name) + " [0-9]+$")
        existing_track_names = {}
        if self.animated_object.animation_data is not None \
                and self.animated_object.animation_data.nla_tracks is not None:
            existing_track_names = {nla_track.name for nla_track in self.animated_object.animation_data.nla_tracks if
                                    nla_track.name == self.track_name or name_plus_number_regex.match(nla_track.name)}

        track_number = 0  # first track is track 1
        existing_tracks = []
        while len(existing_track_names) > 0:
            track_number += 1
            track_name = self.get_track_name(track_number)
            if track_name in existing_track_names:
                existing_track_names.remove(track_name)
            existing_tracks.append(self.get_or_create_nla_track(self.animated_object, track_name, False))
        return existing_tracks

    def get_or_create_nla_track(self, animated_object, track_name: str, create_track_if_not_exists: bool = True):
        if self.action.id_root == "NODETREE" and not isinstance(animated_object, bpy.types.NodeTree):
            animation_data = ObjectUtils.get_or_create_animation_data(animated_object.node_tree)
        else:
            animation_data = ObjectUtils.get_or_create_animation_data(animated_object)
        for track in animation_data.nla_tracks:
            if track.name == track_name:
                return track
        if not create_track_if_not_exists:
            return None
        else:
            nla_track = animation_data.nla_tracks.new()
            nla_track.name = track_name
            return nla_track

    def get_track_name(self, track_number: int):
        return self.track_name if track_number == 1 else f"{self.track_name} {track_number}"

    def duplicated_object(self):
        # this method assumes no objects are selected when called
        # neither the original object nor the duplicated object will be selected when this method returns
        if self.action.id_root == "OBJECT":
            return ObjectUtils.duplicate_object(self.animated_object, self.context)
        else:
            if self.objects_using_data is None:
                object_type = self.action.id_root
                self.objects_using_data = [x for x in self.context.blend_data.objects if
                                           x.type == object_type and x.data == self.animated_object]
            if len(self.objects_using_data) == 0:
                return None  # no objects to duplicate

            duplicated_object = ObjectUtils.duplicate_object(self.objects_using_data[0], self.context)
            # create linked duplicates for any other objects using the data
            for x in self.objects_using_data[1:]:
                ObjectUtils.duplicate_object(x, self.context, linked=True)
            return duplicated_object.data


class NoteActionCopier:

    def __init__(self, note_action_property, context, instrument_track_name: Optional[str], additional_frame_offset=0):
        self.context = context
        self.additional_frame_offset = additional_frame_offset
        self.context = context
        self.note_action_property = note_action_property
        self.duplicate_on_overlap = midi_data.id_type_is_object(note_action_property.id_type) and \
                                    note_action_property.on_overlap == "DUPLICATE_OBJECT"
        self.action = note_action_property.action
        self.filter_groups_property = note_action_property.note_filter_groups
        self.add_filters = note_action_property.add_filters
        self.blend_mode: str = note_action_property.blend_mode
        self.skip_overlaps: bool = note_action_property.on_overlap == "SKIP"
        self.note_action_track_name: str = note_action_property.nla_track_name
        self.instrument_track_name = instrument_track_name

        self.id_type = note_action_property.id_type
        animated_object_property = midi_data.ID_PROPERTIES_DICTIONARY[self.id_type][0]
        self.animated_object = getattr(note_action_property, animated_object_property)

    def copy_notes(self, notes: List[Note], track_name: str, note_id: str):
        if not notes:
            return  # no notes to copy, do nothing

        nla_tracks = NlaTracksManager(action=self.action,
                                      track_name=track_name,
                                      animated_object=self.animated_object,
                                      context=self.context,
                                      duplicate_on_overlap=self.duplicate_on_overlap,
                                      blend_mode=self.blend_mode,
                                      skip_overlaps=self.skip_overlaps)

        loaded_midi_data = midi_data.get_midi_data(MidiDataType.NLA)
        action = self.note_action_property.action
        non_scaled_action_length = None if action is None else action.frame_range[1] - action.frame_range[0]

        note_overlap_strategy = NoteCollectionOverlapStrategy(not self.duplicate_on_overlap, self.duplicate_on_overlap,
                                                              False)
        note_collection_filter = NoteCollectionFilter(self.filter_groups_property,
                                                      PitchUtils.note_pitch_from_id(note_id), True,
                                                      self.add_filters, self.context)
        note_collection_meta_data = NoteCollectionMetaData.from_note_action_property(
            loaded_midi_data, self.context, self.note_action_property, non_scaled_action_length,
            additional_frame_offset=self.additional_frame_offset,
            override_action_length=self.note_action_property.action_length if self.duplicate_on_overlap else None)
        existing_note_overlaps = ExistingNoteOverlaps(
            nla_tracks.existing_tracks_list(), lambda nla_track: nla_track.strips,
            lambda nla_strip: (nla_strip.frame_start, nla_strip.frame_end))

        note_collection = NoteCollection(notes, note_collection_meta_data, note_overlap_strategy,
                                         note_collection_filter, existing_note_overlaps)
        nla_tracks.copy_notes_to_tracks(note_collection)
        return

    def copy_notes_to_object(self, track_id, note_id: str):
        if self.action is None or self.animated_object is None:
            return
        track_name = self.note_action_track_name
        if track_name is None or len(track_name) == 0:
            track_name = self.instrument_track_name if self.instrument_track_name else \
                PitchUtils.note_display_from_pitch(
                    PitchUtils.note_pitch_from_id(note_id),
                    midi_data.get_midi_data(MidiDataType.NLA).get_middle_c_id(
                        self.context)) + " - " + midi_data.get_midi_data(MidiDataType.NLA).get_displayed_track_name(
                    track_id)
        notes = midi_data.MidiDataUtil.get_notes(track_id, midi_data.get_midi_data(MidiDataType.NLA))

        self.copy_notes(notes, track_name, note_id)

    def copy_notes_to_objects(self, track_id: str, note_id: str, objects):
        for x in objects:
            self.animated_object = x
            self.copy_notes_to_object(track_id, note_id)

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


class NLAMidiCopier(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
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
        note_action_property = midi_data.get_midi_data(MidiDataType.NLA).selected_note_action_property(context)

        id_type = note_action_property.id_type

        selected_objects = context.selected_objects if midi_data.can_resolve_data_from_selected_objects(id_type) else []
        for x in selected_objects:
            x.select_set(False)
        note_action_copier = NoteActionCopier(note_action_property, context, None)

        if note_action_property.copy_to_selected_objects and midi_data.can_resolve_data_from_selected_objects(id_type):
            action_id_root = midi_data.ID_PROPERTIES_DICTIONARY[id_type][1]
            objects_to_copy = ObjectUtils.data_from_objects(selected_objects, action_id_root)
            loaded_midi_data = midi_data.get_midi_data(MidiDataType.NLA)
            note_action_copier.copy_notes_to_objects(loaded_midi_data.get_track_id(context),
                                                     loaded_midi_data.get_note_id(context), objects_to_copy)
        elif note_action_copier.animated_object is not None:
            loaded_midi_data = midi_data.get_midi_data(MidiDataType.NLA)
            note_action_copier.copy_notes_to_object(loaded_midi_data.get_track_id(context),
                                                    loaded_midi_data.get_note_id(context))

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
        instrument = midi_data.get_midi_data(MidiDataType.NLA).selected_instrument(context)
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


class NLABulkMidiCopier(bpy.types.Operator, OperatorUtils.DynamicTooltipOperator):
    """
    This operator handles both copying to an instrument and copying to notes from the bulk copy panel.
    """
    bl_idname = "ops.nla_bulk_midi_copier"
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
        quick_copy_tool = context.scene.midi_data_property.bulk_copy_property.quick_copy_tool
        if quick_copy_tool == "copy_along_path":
            NLABulkMidiCopier.notes_along_path(context)
        elif quick_copy_tool == "copy_by_object_name":
            NLABulkMidiCopier.notes_by_object_name(context)
        else:
            NLABulkMidiCopier.single_note_to_instrument(context)

    @staticmethod
    def single_note_to_instrument(context):
        midi_panel_note_action_property = context.scene.midi_data_property.note_action_property
        note_pitch: int = int(context.scene.midi_data_property.copy_to_instrument_selected_note_id)
        NLABulkMidiCopier.animate_or_copy_to_instrument(True,
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
        midi_data_property = midi_data.get_midi_data(MidiDataType.NLA).get_midi_data_property(context)
        note_action_property = midi_data_property.note_action_property
        action_id_root = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][1]

        animated_objects = ObjectUtils.data_from_objects(objs, action_id_root)

        notes_to_copy = NLABulkMidiCopier.notes_to_copy(midi_data_property.bulk_copy_property,
                                                        midi_data.get_midi_data(MidiDataType.NLA))

        NLABulkMidiCopier.animate_objects(notes_to_copy, animated_objects, note_action_property,
                                          bulk_copy_property.copy_to_instrument,
                                          context)

    @staticmethod
    def animate_objects(notes_to_copy: List[str], objects_to_animate, note_action_property, copy_to_instrument: bool,
                        context):
        NLABulkMidiCopier.animate_note_object_paris(zip(notes_to_copy, objects_to_animate),
                                                    note_action_property, copy_to_instrument, context)

    @staticmethod
    def animate_note_object_paris(note_object_pairs, note_action_property, copy_to_instrument: bool, context):
        note_action_object_field: str = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][0]
        original_object_value = getattr(note_action_property, note_action_object_field)

        note_action_object_field = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][0]

        for note_to_copy, animated_object in note_object_pairs:
            setattr(note_action_property, note_action_object_field, animated_object)
            NLABulkMidiCopier.animate_or_copy_to_instrument(copy_to_instrument, note_to_copy,
                                                            note_action_property, context)

        # set the note action property object back to what is was when the copy button was pressed
        setattr(note_action_property, note_action_object_field, original_object_value)

    @staticmethod
    def notes_by_object_name(context):
        loaded_midi_data = midi_data.get_midi_data(MidiDataType.NLA)
        midi_data_property = loaded_midi_data.get_midi_data_property(context)
        note_action_property = midi_data_property.note_action_property
        bulk_copy_property = midi_data_property.bulk_copy_property
        action_id_root = midi_data.ID_PROPERTIES_DICTIONARY[note_action_property.id_type][1]
        animated_objects_dict = ObjectUtils.data_dict_from_objects(
            context.selected_objects if bulk_copy_property.selected_objects_only else context.scene.objects,
            action_id_root)
        data_name_pairs = [(x[0], x[1].name) for x in animated_objects_dict.items()]
        note_object_pairs = []
        match_by_track_name = bulk_copy_property.copy_by_name_type == "copy_by_track_and_note"
        track_name = midi_data_property.track_list if match_by_track_name else None
        displayed_track_name = loaded_midi_data.get_displayed_track_name(track_name) if track_name is not None else None

        notes_enum_list = loaded_midi_data.notes_list
        for note_enum in notes_enum_list:
            for data_name_pair in data_name_pairs:
                if NLABulkMidiCopier.note_matches_object_name(note_enum, data_name_pair[1], displayed_track_name):
                    note_object_pairs.append((note_enum[0], data_name_pair[0]))
        NLABulkMidiCopier.animate_note_object_paris(note_object_pairs, note_action_property,
                                                    bulk_copy_property.copy_to_instrument,
                                                    context)

    @staticmethod
    def note_matches_object_name(note_enum, object_name: str, displayed_track_name: str = None):
        if displayed_track_name is not None and displayed_track_name not in object_name:
            return False
        object_name_lower: str = object_name.strip().lower()
        note_name: str = note_enum[1].lower()
        return object_name_lower.startswith(note_name) or object_name_lower.endswith(note_name)

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
            scale_pitch = PitchUtils.SCALE_TO_PITCH_MAP[bulk_copy_property.scale_filter_scale]

        while note_pitch <= 127:
            note_id: str = PitchUtils.note_id_from_pitch(note_pitch)
            passes_scale_filter = PitchUtils.note_in_scale(note_pitch, scale_pitch) == in_scale \
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
        loaded_midi_data.selected_instrument_for_copy_to_id(), otherwise copies the action using the given note
        :param note_id: note to copy to
        :param note_action_property: the note action property
        :param context: the context
        """
        if copy_to_instrument:
            instrument = midi_data.get_midi_data(MidiDataType.NLA).selected_instrument_for_copy_to_id(context)
            if instrument is None:
                return
            copied_note_action_property = PropertyUtils.get_note_action_property(instrument,
                                                                                 PitchUtils.note_pitch_from_id(note_id))
            midi_panel_note_action_property = context.scene.midi_data_property.note_action_property
            PropertyUtils.copy_note_action_property(midi_panel_note_action_property, copied_note_action_property,
                                                    midi_data.ID_PROPERTIES_DICTIONARY)
        else:
            NoteActionCopier(note_action_property, context, None) \
                .copy_notes_to_object(midi_data.get_midi_data(MidiDataType.NLA).get_track_id(context), note_id)
