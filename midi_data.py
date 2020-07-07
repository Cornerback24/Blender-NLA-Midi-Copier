from .midi_analysis.MidiData import MidiData
from . import PitchUtils
from . import PropertyUtils
import math


# noinspection PyUnusedLocal
def get_tracks_list(self, context):
    return midi_data.get_tracks_list(self, context)


def get_track_id(context):
    return midi_data.get_track_id(context)


def get_note_id(context) -> str:
    return midi_data.get_note_id(context)


def get_instruments(midi_data_property, context):
    return midi_data.get_instruments(midi_data_property, context)


def get_instrument_notes(instrument_property, context):
    return midi_data.get_instrument_notes(instrument_property, instrument_property.note_search_string.strip(),
                                          LoadedMidiData.store_notes_list_one)


def get_selected_instrument_notes(midi_data_property, context):
    return midi_data.get_instrument_notes(midi_data.selected_instrument_for_copy_to_id(context),
                                          midi_data_property.copy_to_instrument_note_search_string,
                                          LoadedMidiData.store_notes_list_two)


def selected_instrument(context):
    return midi_data.selected_instrument(context)


# key is display name, value is (NoteActionProperty field name, Action id_root, enum number)
ID_PROPERTIES_DICTIONARY = {"Armature": ("armature", "ARMATURE", 0),
                            "Brush": ("brush", "BRUSH", 18),
                            # "Action": ("action", "ACTION),
                            "Camera": ("camera", "CAMERA", 1),
                            # "Cache File": ("cachefile", "CACHEFILE"),
                            "Collection": ("collection", "COLLECTION", 19),
                            "Curve": ("curve", "CURVE", 2),
                            # "Font": ("font", "FONT"),
                            "Grease Pencil": ("greasepencil", "GREASEPENCIL", 3),
                            "Image": ("image", "IMAGE", 20),
                            "Key": ("key", "KEY", 4),
                            "Lattice": ("lattice", "LATTICE", 5),
                            # "Library": ("library", "LIBRARY"),
                            "Light": ("light", "LIGHT", 6),
                            "Light Probe": ("light_probe", "LIGHT_PROBE", 7),
                            # "Linestyle": ("linestyle", "LINESTYLE"),
                            "Mask": ("mask", "MASK", 8),
                            "Material": ("material", "MATERIAL", 9),
                            "MetaBall": ("meta", "META", 10),
                            "Mesh": ("mesh", "MESH", 11),
                            "Movie Clip": ("movieclip", "MOVIECLIP", 12),
                            # "Node Tree": ("nodetree", "NODETREE"),
                            "Object": ("object", "OBJECT", 13),
                            "Paintcurve": ("paintcurve", "PAINTCURVE", 21),
                            "Palette": ("palette", "PALETTE", 22),
                            # "Particle": ("particle", "PARTICLE"),
                            "Scene": ("scene", "SCENE", 14),
                            "Sound": ("sound", "SOUND", 23),
                            "Speaker": ("speaker", "SPEAKER", 15),
                            "Text": ("text", "TEXT", 24),
                            "Texture": ("texture", "TEXTURE", 16),
                            "Volume": ("volume", "VOLUME", 17),
                            # "Window Manager": ("windowmanager", "WINDOWMANAGER"),
                            # "Workspace": ("workspace", "WORKSPACE"),
                            "World": ("world", "WORLD", 25)}

OBJECT_ID_TYPES = {
    "ARMATURE",
    "CAMERA",
    "CURVE",
    "FONT",
    "GPENCIL",
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
    return ID_PROPERTIES_DICTIONARY[midi_data_id_type][1] in OBJECT_ID_TYPES


# node trees don't show up in the selector,
# so applying an action is done by selecting the object the node tree belongs to
node_tree_types = "MATERIAL, TEXTURE, WORLD, SCENE, LIGHT"

NO_INSTRUMENT_SELECTED = "[No Instrument Selected]"

BLEND_MODES = [("None", "None (skip overlaps)", "No blending. Overlapping strips are not copied", 0),
               ("REPLACE", "Replace", "Replace", 1),
               ("COMBINE", "Combine", "Combine", 2),
               ("ADD", "Add", "Add", 3),
               ("SUBTRACT", "Subtract", "Subtract", 4),
               ("MULTIPLY", "Multiply", "Multiply", 5)]


class MidiDataUtil:
    @staticmethod
    def get_unique_name(name, name_list):
        """
        :param name: name to make unique
        :param name_list: list of names to deconfict with
        :return: the first value of name, name2, name3 that is not in the list
        """
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

        track = next((x for x in loaded_midi_data.midi_data.tracks if x.name == track_id), None)

        notes = [x for x in track.notes]

        notes.sort()
        return notes

    @staticmethod
    def note_length_frames(note, frames_per_second):
        """
        :param note: the Note to get the length of
        :param frames_per_second: project's frames per second
        :return: the length of the note in frames rounded to the nearest frame
        """
        # note.length() is in ms
        return math.floor((note.length() / 1000) * frames_per_second)


class LoadedMidiData:
    def __init__(self, get_midi_data_property):
        """
        :param get_midi_data_property: function to get this property from the context
        """
        self.midi_data = None
        # api documentation says that references to the values returned by callbacks need to be kept around to prevent issues
        self.track_list = []  # list of tracks in the midi file
        self.notes_list = []  # list of notes for the selected midi track
        self.all_notes = []  # enum property list of all notes (0 to 127), enum key is note id
        self.all_notes_for_pitch_filter = []  # enum property list of all notes (0 to 127), enum key is note id
        self.instruments_list = []  # list of defined instruments
        self.instrument_notes_list = []  # list of notes for the selected instrument
        self.instrument_notes_list2 = []  # list of notes for the selected instruments, used for copy to instrument action
        self.instrument_note_actions_list = []  # list of actions for the selected note of the selected instrument
        self.notes_list_dict = {}  # key is track id String, value is list of note properties (where enum property id is note id)
        self.current_midi_filename = None  # name of the loaded midi file
        self.middle_c_id = None  # note id being used for middle c
        self.middle_c_on_last_tracks_update = None  # value of the middle_c_id property when the tracks were updated last
        self.middle_c_on_last_all_notes_update = None  # v alue of the middle_c_id property when the list of all notes updated last
        self.get_midi_data_property = get_midi_data_property

    def update_midi_file(self, midi_filename: str, force_update: bool, context):
        """
        Updates the current midi file
        :param force_update: if true will reload the midi file even if it has the same name
        :param midi_filename: path to the midi file
        """
        if midi_filename is None:
            self.midi_data = None
            return
        elif midi_filename == self.current_midi_filename and not force_update:
            return
        self.current_midi_filename = midi_filename
        self.midi_data = MidiData(midi_filename)
        self.__create_track_list(context)

    def __create_track_list(self, context):
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
                                                     PitchUtils.note_description_from_pitch(pitch, self.middle_c_id))
                                                    for pitch in note_pitches_ordered]
                tracks.append(track_name)
        tracks.sort()
        self.track_list = [(x, x, x) for x in tracks]

    # noinspection PyUnusedLocal
    def get_tracks_list(self, property_self, context):
        """
        :return: list of tracks in the current midi file
        """
        if self.middle_c_on_last_tracks_update != self.get_middle_c_id(context):
            # middle c changed, update display
            self.__create_track_list(context)
        return self.track_list

    # noinspection PyUnusedLocal
    def get_notes_list(self, property_self, context):
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
        # instruments_list = [(x.name, x.name, x.name) for x in midi_data_property.instruments]
        # instruments_list.sort()
        self.instruments_list.sort(key=lambda x: x[1].lower())
        self.instruments_list.insert(0, (NO_INSTRUMENT_SELECTED, "", "No Instrument Selected", 0))

        return self.instruments_list

    def get_instrument_notes(self, instrument_property, search_string, store_and_return_list):
        """
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
                                   note_description + append_to_description))

        new_notes_list = LoadedMidiData.notes_list_filtered(new_notes_list, search_string)
        return store_and_return_list(self, new_notes_list)

    def store_notes_list_one(self, notes_list):
        self.instrument_notes_list = notes_list
        return self.instrument_notes_list

    def store_notes_list_two(self, notes_list):
        self.instrument_notes_list2 = notes_list
        return self.instrument_notes_list2

    @staticmethod
    def notes_list_filtered(notes_list_enums, filter_string):
        filter_string_is_digit = filter_string.isdigit()
        # if digit, then check string equals note pitch, else check note display contains string
        note_filter_lambda = \
            (lambda note: filter_string == note[0]) if filter_string_is_digit else \
                (lambda note: filter_string.lower() in note[1].lower())

        filtered_notes = [note for note in notes_list_enums if note_filter_lambda(note)]
        # to avoid issues with empty enum list, return all if no match instead of none
        return filtered_notes if len(filtered_notes) > 0 else notes_list_enums

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

    def get_all_notes(self, context, for_pitch_filter=False):
        """
        :return: list of all notes (pitches 0 - 127) as enum properties (where enum property id is note id)
        """
        if self.get_middle_c_id(context) != self.middle_c_on_last_all_notes_update:
            self.all_notes = []
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
        return self.all_notes_for_pitch_filter if for_pitch_filter else self.all_notes

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


midi_data = LoadedMidiData(lambda context: context.scene.midi_data_property)
dope_sheet_midi_data = LoadedMidiData(lambda context: context.scene.dope_sheet_midi_data_property)
