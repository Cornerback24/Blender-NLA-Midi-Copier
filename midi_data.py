from enum import Enum
from typing import Optional

from .midi_analysis.MidiData import MidiData
from . import PitchUtils
from . import PropertyUtils

# key is display name, value is (NoteActionProperty field name, Action id_root, enum number)
ID_PROPERTIES_DICTIONARY = {"Armature": ("armature", "ARMATURE", "ARMATURE_DATA", 0),
                            "Brush": ("brush", "BRUSH", "BRUSH_DATA", 18),
                            # "Action": ("action", "ACTION),
                            "Camera": ("camera", "CAMERA", "CAMERA_DATA", 1),
                            # "Cache File": ("cachefile", "CACHEFILE"),
                            "Collection": ("collection", "COLLECTION", "OUTLINER_COLLECTION", 19),
                            "Curve": ("curve", "CURVE", "CURVE_DATA", 2),
                            # "Font": ("font", "FONT"),
                            "Grease Pencil": ("greasepencil", "GREASEPENCIL", "GREASEPENCIL", 3),
                            "Image": ("image", "IMAGE", "IMAGE_DATA", 20),
                            "Key": ("key", "KEY", "SHAPEKEY_DATA", 4),
                            "Lattice": ("lattice", "LATTICE", "LATTICE_DATA", 5),
                            # "Library": ("library", "LIBRARY"),
                            "Light": ("light", "LIGHT", "LIGHT", 6),
                            "Light Probe": ("light_probe", "LIGHT_PROBE", "LIGHTPROBE_CUBEMAP", 7),
                            # "Linestyle": ("linestyle", "LINESTYLE"),
                            "Mask": ("mask", "MASK", "MOD_MASK", 8),
                            "Material": ("material", "MATERIAL", "MATERIAL", 9),
                            "MetaBall": ("meta", "META", "META_DATA", 10),
                            "Mesh": ("mesh", "MESH", "MESH_DATA", 11),
                            "Movie Clip": ("movieclip", "MOVIECLIP", "TRACKER", 12),
                            "Node Tree": ("nodetree", "NODETREE", "NODETREE", 26),
                            "Object": ("object", "OBJECT", "OBJECT_DATA", 13),
                            "Paintcurve": ("paintcurve", "PAINTCURVE", "CURVE_BEZCURVE", 21),
                            "Palette": ("palette", "PALETTE", "RESTRICT_COLOR_ON", 22),
                            "Particle": ("particle_settings", "PARTICLE", "PARTICLES", 27),
                            "Scene": ("scene", "SCENE", "SCENE_DATA", 14),
                            "Sound": ("sound", "SOUND", "SOUND", 23),
                            "Speaker": ("speaker", "SPEAKER", "SPEAKER", 15),
                            "Text": ("text", "TEXT", "TEXT", 24),
                            "Texture": ("texture", "TEXTURE", "TEXTURE", 16),
                            "Volume": ("volume", "VOLUME", "VOLUME_DATA", 17),
                            # "Window Manager": ("windowmanager", "WINDOWMANAGER"),
                            # "Workspace": ("workspace", "WORKSPACE"),
                            "World": ("world", "WORLD", "WORLD_DATA", 25)}

OBJECT_ID_TYPES = {
    "ARMATURE",
    "CAMERA",
    "CURVE",
    "FONT",
    "GREASEPENCIL",
    "LATTICE",
    "LIGHT",
    "LIGHT_PROBE",
    "MESH",
    "META",
    "OBJECT",
    "SPEAKER",
    "VOLUME"
}


def id_type_is_object(midi_data_id_type: str):
    """
    :param midi_data_id_type: the id_type (as defined in NoteActionProperty)
    :return: True if the type corresponds to a Blender Object or a Blender Object.data type
    """
    return ID_PROPERTIES_DICTIONARY[midi_data_id_type][1] in OBJECT_ID_TYPES


def can_resolve_data_from_selected_objects(midi_data_id_type: str):
    """
    :param midi_data_id_type: the id_type (as defined in NoteActionProperty)
    :return: True if the type corresponds to a data type that can be resolved for each object
     given the scene's selected objects.(For example, True for mesh since an object's mesh can be found using
     object.data.)
    """
    return id_type_is_object(midi_data_id_type) or midi_data_id_type == "Material" or midi_data_id_type == "Key"


# node trees don't show up in the selector,
# so applying an action is done by selecting the object the node tree belongs to
node_tree_types = "MATERIAL, TEXTURE, WORLD, SCENE, LIGHT"

NO_INSTRUMENT_SELECTED = "[No Instrument Selected]"

# "None" is deprecated, replaced with Skip overlap option
BLEND_MODES_DEPRECATED = [("None", "None (skip overlaps)", "No blending. Overlapping strips are not copied", 0),
                          ("REPLACE", "Replace", "Replace", 1),
                          ("COMBINE", "Combine", "Combine", 2),
                          ("ADD", "Add", "Add", 3),
                          ("SUBTRACT", "Subtract", "Subtract", 4),
                          ("MULTIPLY", "Multiply", "Multiply", 5)]

BLEND_MODES = [x for x in BLEND_MODES_DEPRECATED if x[0] != "None"]


class MidiDataUtil:
    @staticmethod
    def get_unique_name(name, name_list):
        """
        :param name: name to make unique
        :param name_list: list of names to deconfict with
        :return: the first value of name, name2, name3 that is not in the list
        """
        # null characters in strings can prevent the enum property from working
        name = name.strip('\x00')
        if len(name) == 0:
            name = "Track"
        if name not in name_list:
            return name
        else:
            number = 2
            unique_name = name + " (" + str(number) + ")"
            while unique_name in name_list:
                number += 1
                unique_name = name + " (" + str(number) + ")"
            return unique_name

    @staticmethod
    def get_notes(track_id: str, loaded_midi_data):
        """
        :param track_id: name of the track to get the notes from
        :param loaded_midi_data: LoadedMidiData instance
        :return: list of all of the notes from the loaded midi file matching the track, sorted by time
        """

        track = loaded_midi_data.tracks_dict[track_id]

        notes = [x for x in track.notes]

        notes.sort()
        return notes


class LoadedMidiData:
    def __init__(self, get_midi_data_property, midi_data_type: int):
        """
        :param get_midi_data_property: function to get this property from the context
        """
        self.midi_data = None  # the MidiData object representing the midi file
        self.midi_data_type = midi_data_type
        # api documentation says that references to the values returned by callbacks need to be kept around to prevent issues
        self.track_list = []  # list of tracks in the midi file
        self.tracks_dict = {}  # map track name to midi track
        self.notes_list = []  # list of notes for the selected midi track
        self.all_notes = []  # enum property list of all notes (0 to 127), enum key is note id
        self.all_notes_for_pitch_filter = []  # enum property list of all notes (0 to 127), enum key is note id
        self.instruments_list = []  # list of defined instruments
        self.instrument_notes_list = []  # list of notes for the selected instrument
        self.instrument_notes_list2 = []  # list of notes for the selected instruments, used for copy to instrument action
        self.instrument_note_actions_list = []  # list of actions for the selected note of the selected instrument
        self.all_notes_list = []  # list of all notes (midi pitches 0 to 127)
        self.notes_list_dict = {}  # key is track id String, value is list of note properties (where enum property id is note id)
        self.current_midi_filename = None  # name of the loaded midi file
        self.middle_c_id = None  # note id being used for middle c
        self.middle_c_on_last_tracks_update = None  # value of the middle_c_id property when the tracks were updated last
        self.middle_c_on_last_all_notes_update = None  # value of the middle_c_id property when the list of all notes updated last
        self.get_midi_data_property = get_midi_data_property
        self.ms_per_tick = None  # ms per tick, used if not using file tempo
        self.use_file_tempo = True  # whether to use the file tempo or the tempo property

    def update_midi_file(self, midi_filename: Optional[str], force_update: bool, context,
                         called_on_script_reload: bool = False):
        """
        Updates the current midi file
        :param force_update: if true will reload the midi file even if it has the same name
        :param midi_filename: path to the midi file
        :param context: the contet
        :param called_on_script_reload: If False, update properties such as the file's tempo information to be
        displayed in the midi settings panel. Updating properties is not allowed in the context if this is called
        because of a script reload.
        """
        if midi_filename is None:
            self.midi_data = None
            return
        elif midi_filename == self.current_midi_filename and not force_update:
            return
        self.current_midi_filename = midi_filename
        self.midi_data = MidiData(midi_filename)
        if not called_on_script_reload:
            if self.midi_data.isTicksPerBeat:
                # need to access properties with dictionary style because they are read-only
                self.get_midi_data_property(context).tempo_settings["file_beats_per_minute"] = \
                    60000 / self.midi_data.msPerBeat
                self.get_midi_data_property(context).tempo_settings["file_ticks_per_beat"] = self.midi_data.ticksPerBeat
            else:
                # midi file is in frames per second instead of beats per minute
                # for simplicity, display values in ticks per second using one beat per second
                # (most midi files will be in beats per minute, not frames per second)
                self.get_midi_data_property(context).tempo_settings["file_beats_per_minute"] = 60
                self.get_midi_data_property(context).tempo_settings[
                    "file_ticks_per_beat"] = self.midi_data.ticksPerSecond

        # reloading track names involves updating properties which is not allowed in context if called on script reload
        self.__create_track_list(context, not called_on_script_reload)
        if not called_on_script_reload:
            # call update track list function to update selected note
            if len(self.track_list) > 0:
                self.get_midi_data_property(context).track_list = self.track_list[0][0]
        self.update_tempo(context)

    def update_tempo(self, context):
        tempo_property = self.get_midi_data_property(context).tempo_settings
        self.use_file_tempo = tempo_property.use_file_tempo
        ticks_per_beat = tempo_property.file_ticks_per_beat if tempo_property.use_file_ticks_per_beat \
            else tempo_property.ticks_per_beat
        beats_per_minute = tempo_property.beats_per_minute
        if ticks_per_beat > 0 and beats_per_minute > 0:
            self.ms_per_tick = 60000 / (ticks_per_beat * beats_per_minute)

    def __create_track_list(self, context, reload_names_from_file: bool = False):
        def __displayed_track_name(track_name_overrides, name):
            track_name_override = track_name_overrides[name] if name in track_name_overrides else name
            return track_name_override if len(track_name_override.strip()) > 0 else name

        self.notes_list_dict = {}
        tracks = []
        self.track_list = []
        self.middle_c_on_last_tracks_update = self.get_middle_c_id(context)
        for track in self.midi_data.tracks:
            if len(track.notes) > 0:
                track_name = MidiDataUtil.get_unique_name(track.name, tracks)
                notes_pitches_set = {note.pitch for note in track.notes}
                note_pitches_ordered = sorted(notes_pitches_set)
                self.notes_list_dict[track_name] = [(PitchUtils.note_id_from_pitch(pitch),
                                                     PitchUtils.note_display_from_pitch(pitch, self.middle_c_id),
                                                     PitchUtils.note_description_from_pitch(pitch, self.middle_c_id),
                                                     pitch)
                                                    for pitch in note_pitches_ordered]
                tracks.append(track_name)
                self.tracks_dict[track_name] = track
        tracks.sort()
        displayed_track_names = self.get_midi_data_property(context).midi_track_properties
        existing_track_name_overrides = {x.midi_track_name: x.displayed_track_name for x in
                                         displayed_track_names}

        if reload_names_from_file:
            # create track name properties to match the midi file, keep any existing that match
            displayed_track_names.clear()
            for track in tracks:
                midi_track_property = displayed_track_names.add()
                midi_track_property.midi_track_name = track
                midi_track_property.midi_data_type = self.midi_data_type
                if track in existing_track_name_overrides:
                    midi_track_property.displayed_track_name = existing_track_name_overrides[track]

        self.track_list = [(x, __displayed_track_name(existing_track_name_overrides, x), x, tracks.index(x)) for x in
                           tracks]
        self.track_list.sort(key=lambda x: x[1].lower())

    # noinspection PyUnusedLocal
    def get_tracks_list(self, property_self, context):
        """
        :return: list of tracks in the current midi file
        """
        if self.midi_data is None:
            # if midi_data is None here, it is probably because scripts were reloaded in blender
            # (on_load is not called in that case, so need to read in the midi file here)
            self.update_midi_file(self.get_midi_data_property(context).midi_file, False, context, True)
            self.__create_track_list(context)
        elif self.middle_c_on_last_tracks_update != self.get_middle_c_id(context):
            # middle c changed, update display
            self.__create_track_list(context)
        return self.track_list

    def update_track_names(self, context):
        self.__create_track_list(context)

    def get_notes_list(self, context):
        """
        :return: list of notes for the current selected track
        """
        track_id = self.get_midi_data_property(context).track_list
        self.notes_list = self.notes_list_dict.get(track_id, [])
        return self.notes_list

    def get_track_id(self, context):
        """
        :return: the name of the selected track
        """
        return self.get_midi_data_property(context).track_list

    def get_note_id(self, context) -> str:
        """
        :return: the name of the selected note (such as "C4")
        """
        return self.get_midi_data_property(context).notes_list

    def selected_note_action_property(self, context):
        return self.get_midi_data_property(context).note_action_property

    def get_instruments(self, midi_data_property, context):
        """
        :return: The list of instruments for the selected_instrument_id EnumProperty
        """
        self.instruments_list.clear()
        for i in range(len(midi_data_property.instruments)):
            instrument = midi_data_property.instruments[i]
            # identifier is the index of the instrument in midi_data_property.instruments
            # explicitly define the number so that if a rename changes the position in the returned list,
            # the selected instrument is preserved
            self.instruments_list.append((str(i), instrument.name, instrument.name, i + 1))
        self.instruments_list.sort(key=lambda x: x[1].lower())
        self.instruments_list.insert(0, (NO_INSTRUMENT_SELECTED, "", "No Instrument Selected", 0))

        return self.instruments_list

    def get_instrument_notes(self, instrument_property, store_and_return_list):
        """
        :param instrument_property the property for the instrument to get the notes from
        :param store_and_return_list lambda that stores the notes to a field in this LoadedMidiData instance
        and returns the stored list
        :return: list of notes for the instrument's selected_note_id EnumProperty (where enum property id is note pitch)
        """
        new_notes_list = []
        if instrument_property is None:
            return store_and_return_list(self, new_notes_list)

        instrument_notes_action_dictionary = {}
        for x in instrument_property.notes:
            instrument_notes_action_dictionary[x.note_id] = x.actions
        for pitch in range(128):
            note_display = PitchUtils.note_display_from_pitch(pitch, self.middle_c_id)
            append_to_note = ""
            append_to_description = ""
            if pitch in instrument_notes_action_dictionary:
                actions_for_note = instrument_notes_action_dictionary.get(pitch)
                action_count_for_note = len(actions_for_note)
                note_display += " (" + str(action_count_for_note) + ")"
                if LoadedMidiData.__instrument_filters_may_not_match_pitch(actions_for_note, pitch):
                    append_to_note = " *"
                    append_to_description = "\n* Some actions have filters that may pitch different pitches"
                if LoadedMidiData.__contains_incomplete_action(actions_for_note):
                    append_to_note = append_to_note + " !"
                    append_to_description = append_to_description + "\n! Some actions are missing an object or action"
            note_description = PitchUtils.note_description_from_pitch(pitch, self.middle_c_id)
            new_notes_list.append((str(pitch), note_display + append_to_note,
                                   note_description + append_to_description, pitch))

        return store_and_return_list(self, new_notes_list)

    def get_all_notes_list(self):
        """
        :return: a list of notes to select (all pitches 0  to 127)
        """
        self.all_notes_list = []
        for pitch in range(128):
            note_display = PitchUtils.note_display_from_pitch(pitch, self.middle_c_id)
            note_description = PitchUtils.note_description_from_pitch(pitch, self.middle_c_id)
            self.all_notes_list.append((str(pitch), note_display, note_description, pitch))

        return self.all_notes_list

    def store_notes_list_one(self, notes_list):
        self.instrument_notes_list = notes_list
        return self.instrument_notes_list

    def store_notes_list_two(self, notes_list):
        self.instrument_notes_list2 = notes_list
        return self.instrument_notes_list2

    @staticmethod
    def __instrument_filters_may_not_match_pitch(actions, pitch: int) -> bool:
        for action in actions:
            if action.add_filters:
                if LoadedMidiData.__filters_may_not_match_pitch(action, pitch):
                    return True
        return False

    @staticmethod
    def __filters_may_not_match_pitch(action, pitch: int) -> bool:
        for filter_group in action.note_filter_groups:
            pitch_filters = [note_filter for note_filter in filter_group.note_filters if
                             note_filter.filter_type == "note_pitch_filter"]
            if len(pitch_filters) > 0:
                final_filter = pitch_filters[-1]
                #  check if the last applied pitch filter is equal to selected note
                if not (final_filter.comparison_operator == "equal_to" and (
                        PitchUtils.note_id_is_selected_note(final_filter.note_pitch) or
                        PitchUtils.note_pitch_from_id(final_filter.note_pitch) == pitch)):
                    return True
                # last applied pitch filter is equal to selected note, check if any previous filters filter selected
                # note out
                for pitch_filter in pitch_filters:
                    if PitchUtils.note_id_is_selected_note(final_filter.note_pitch):
                        filter_pitch = pitch
                    else:
                        filter_pitch = PitchUtils.note_pitch_from_id(pitch_filter.note_pitch)
                    if not PropertyUtils.compare(pitch_filter.comparison_operator, pitch, filter_pitch):
                        return True
        return False

    @staticmethod
    def __contains_incomplete_action(actions):
        for action in actions:
            if action.action is None:
                return True
            animated_object_property = ID_PROPERTIES_DICTIONARY[action.id_type][0]
            animated_object = getattr(action, animated_object_property)
            if animated_object is None:
                return True
        return False

    def get_all_notes_for_pitch_filter(self, context):
        """
        :param context the context
        :return: list of all notes (pitches 0 - 127) as enum properties (where enum property id is note id)
        """
        if self.get_middle_c_id(context) != self.middle_c_on_last_all_notes_update:
            self.all_notes_for_pitch_filter = []
            self.middle_c_on_last_all_notes_update = self.get_middle_c_id(context)
            for pitch in range(128):
                note_display = PitchUtils.note_display_from_pitch(pitch, self.middle_c_id)
                note_description = PitchUtils.note_description_from_pitch(pitch, self.middle_c_id)
                note_enum = (PitchUtils.note_id_from_pitch(pitch), note_display, note_description)
                self.all_notes.append(note_enum)
                self.all_notes_for_pitch_filter.append(note_enum)
            self.all_notes_for_pitch_filter.append(("selected", "Selected",
                                                    "The selected pitch in the Midi panel, or the pitch corresponding "
                                                    "to the instrument note if this filter is part of an instrument"))
        return self.all_notes_for_pitch_filter

    def get_middle_c_id(self, context):
        if self.middle_c_id is None:
            self.middle_c_id = self.get_midi_data_property(context).middle_c_note
        return self.middle_c_id

    def selected_instrument(self, context):
        """
        :param context: the context
        :return: the selected instrument (None if no instrument is selected)
        """
        instrument_id = self.selected_instrument_id(context)
        if instrument_id is not None:
            return self.get_midi_data_property(context).instruments[int(instrument_id)]
        return None

    def selected_instrument_id(self, context):
        """
        :param context: the context
        :return: the id of the selected instrument (None if no instrument selected)
        """
        instrument_id = self.get_midi_data_property(context).selected_instrument_id
        if instrument_id is not None and len(instrument_id) > 0 \
                and instrument_id != NO_INSTRUMENT_SELECTED:
            return instrument_id
        return None

    def selected_instrument_for_copy_to_id(self, context):
        """
        :param context: the context
        :return: the instrument to copy the action to (None if no instrument selected)
        """
        instrument_id = self.get_midi_data_property(context).copy_to_instrument_selected_instrument
        if instrument_id is not None and len(instrument_id) > 0 \
                and instrument_id != NO_INSTRUMENT_SELECTED:
            return self.get_midi_data_property(context).instruments[int(instrument_id)]
        return None


# Effectively an Enum. Doesn't extend Enum because if scripts are reloaded,
# existing values would not match the reloaded class.
class MidiDataType:
    NLA = 1
    DOPESHEET = 2
    GRAPH_EDITOR = 3

    @staticmethod
    def values():
        return [MidiDataType.NLA, MidiDataType.DOPESHEET, MidiDataType.GRAPH_EDITOR]


nla_midi_data = LoadedMidiData(lambda context: context.scene.midi_data_property, MidiDataType.NLA)
dope_sheet_midi_data = LoadedMidiData(lambda context: context.scene.dope_sheet_midi_data_property,
                                      MidiDataType.DOPESHEET)
graph_editor_midi_data = LoadedMidiData(lambda context: context.scene.graph_editor_midi_data_property,
                                        MidiDataType.GRAPH_EDITOR)


def get_midi_data(midi_data_type: MidiDataType) -> LoadedMidiData:
    if midi_data_type == MidiDataType.NLA:
        return nla_midi_data
    elif midi_data_type == MidiDataType.DOPESHEET:
        return dope_sheet_midi_data
    elif midi_data_type == MidiDataType.GRAPH_EDITOR:
        return graph_editor_midi_data


def get_midi_data_property(midi_data_type: int, context):
    return get_midi_data(midi_data_type).get_midi_data_property(context)
