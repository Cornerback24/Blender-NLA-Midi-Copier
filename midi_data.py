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
    return midi_data.get_instrument_notes(instrument_property, context)


def selected_instrument(context):
    return midi_data.selected_instrument(context)


# key is display name, value is (NoteActionProperty field name, Action id_root)
ID_PROPERTIES_DICTIONARY = {"Armature": ("armature", "ARMATURE"),
                            "Camera": ("camera", "CAMERA"),
                            # "Cache File": ("cachefile", "CACHEFILE"),
                            "Curve": ("curve", "CURVE"),
                            "Grease Pencil": ("greasepencil", "GREASEPENCIL"),
                            "Key": ("key", "KEY"),
                            "Lattice": ("lattice", "LATTICE"),
                            "Light": ("light", "LIGHT"),
                            "Light Probe": ("light_probe", "LIGHT_PROBE"),
                            "Mask": ("mask", "MASK"),
                            "Material": ("material", "MATERIAL"),
                            "MetaBall": ("meta", "META"),
                            "Mesh": ("mesh", "MESH"),
                            "Movie Clip": ("movieclip", "MOVIECLIP"),
                            # "Node Tree": ("nodetree", "NODETREE"),
                            "Object": ("object", "OBJECT"),
                            "Scene": ("scene", "SCENE"),
                            "Speaker": ("speaker", "SPEAKER"),
                            "Texture": ("texture", "TEXTURE"),
                            "World": ("world", "WORLD")}

# node trees don't show up in the selector,
# so applying an action is done by selecting the object the node tree belongs to
note_tree_types = "MATERIAL, TEXTURE, WORLD, SCENE, LIGHT"

NO_INSTRUMENT_SELECTED = "[No Instrument Selected]"


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
        self.instruments_list = []  # list of defined instruments
        self.instrument_notes_list = []  # list of notes for the selected instrument
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

    def get_instrument_notes(self, instrument_property, context):
        """
        :return: list of notes for the instrument's selected_note_id EnumProperty (where enum property id is note pitch)
        """
        instrument_notes_action_dictionary = {}
        for x in instrument_property.notes:
            instrument_notes_action_dictionary[x.note_id] = x.actions
        self.instrument_notes_list.clear()
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
            note_description = PitchUtils.note_description_from_pitch(pitch, self.middle_c_id)
            self.instrument_notes_list.append((str(pitch), note_display + append_to_note,
                                               note_description + append_to_description))

        return self.instrument_notes_list

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
                filter_pitch = PitchUtils.note_pitch_from_id(final_filter.note_pitch)
                if not (final_filter.comparison_operator == "equal_to" and filter_pitch == pitch):
                    return True
                for pitch_filter in pitch_filters:
                    filter_pitch = PitchUtils.note_pitch_from_id(pitch_filter.note_pitch)
                    if not PropertyUtils.compare(pitch_filter.comparison_operator, pitch, filter_pitch):
                        return True
        return False

    @staticmethod
    def __contains_incomplete_action(actions):
        for action in actions:
            if action.action is None:
                return True

    def get_all_notes(self, context):
        """
        :return: list of all notes (pitches 0 - 127) as enum properties (where enum property id is note id)
        """
        if self.get_middle_c_id(context) != self.middle_c_on_last_all_notes_update:
            self.all_notes = []
            self.middle_c_on_last_all_notes_update = self.get_middle_c_id(context)
            for pitch in range(128):
                note_display = PitchUtils.note_display_from_pitch(pitch, self.middle_c_id)
                note_description = PitchUtils.note_description_from_pitch(pitch, self.middle_c_id)
                self.all_notes.append((PitchUtils.note_id_from_pitch(pitch), note_display, note_description))
        return self.all_notes

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


midi_data = LoadedMidiData(lambda context: context.scene.midi_data_property)
dope_sheet_midi_data = LoadedMidiData(lambda context: context.scene.dope_sheet_midi_data_property)
