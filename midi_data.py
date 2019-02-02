from .midi_analysis.Note import Note
from .midi_analysis.MidiData import MidiData

midi_data = None
# api documentation says that references to the values returned by callbacks need to be kept around to prevent issues
track_list = []
notes_list = []
notes_list_dict = {}  # key is track id String, value is list of note properties

current_midi_filename = None


def update_midi_file(midi_filename, force_update):
    """
    Updates the current midi file
    :param force_update: if true will reload the midi file even if it has the same name
    :param midi_filename: path to the midi file
    """
    global midi_data
    global notes_list_dict
    global track_list
    global current_midi_filename
    if midi_filename is None:
        midi_data = None
        return
    elif midi_filename == current_midi_filename and not force_update:
        return
    current_midi_filename = midi_filename
    midi_data = MidiData(midi_filename)

    def note_pitch_from_string(pitch_string):
        for int_pitch, string in Note.PITCH_DICTIONARY.items():
            if string == pitch_string:
                return int_pitch
        return 0

    def get_unique_name(name, name_list):
        if name not in name_list:
            return name
        else:
            number = 2
            unique_name = name + " (" + str(number) + ")"
            while unique_name in name_list:
                number += 1
                unique_name = name + " (" + str(number) + ")"
            return unique_name

    notes_list_dict = {}
    tracks = []
    track_list = []
    for track in midi_data.tracks:
        if len(track.notes) > 0:
            track_name = get_unique_name(track.name, tracks)
            notes_list_set = {Note.PITCH_DICTIONARY[x.pitch] for x in track.notes}
            notes_list_set_sorted = sorted(notes_list_set, key=lambda x: note_pitch_from_string(x))
            notes_list_dict[track_name] = [(x, x, x) for x in notes_list_set_sorted]
            tracks.append(track_name)
    tracks.sort()
    track_list = [(x, x, x) for x in tracks]


# noinspection PyUnusedLocal
def get_tracks_list(self, context):
    """
    :return: list of tracks in the current midi file
    """
    global track_list
    return track_list


# noinspection PyUnusedLocal
def get_notes_list(self, context):
    """
    :return: list of notes for the current selected track
    """
    global midi_data
    global notes_list
    track_id = context.scene.midi_data_property.track_list
    notes_list = notes_list_dict.get(track_id, [])
    return notes_list


def get_selected_notes(context):
    """
    :return: list of all of the notes from the current midi file matching the currently selected track and note,
    sorted by time
    """
    track_id = context.scene.midi_data_property.track_list
    note_id = context.scene.midi_data_property.notes_list

    track = None
    for x in midi_data.tracks:
        if x.name == track_id:
            track = x

    notes = []
    if track is not None:
        for x in track.notes:
            if Note.PITCH_DICTIONARY[x.pitch] == note_id:
                notes.append(x)

    notes.sort()
    return notes


def get_track_id(context):
    return context.scene.midi_data_property.track_list


def get_note_id(context):
    return context.scene.midi_data_property.notes_list


# key is display name, value is (NoteActionProperty field name, Action id_root)
ID_PROPERTIES_DICTIONARY = {"Armature": ("armature", "ARMATURE"),
                            "Camera": ("camera", "CAMERA"),
                            "Cache File": ("cachefile", "CACHEFILE"),
                            "Curve": ("curve", "CURVE"),
                            "Grease Pencil": ("greasepencil", "GREASEPENCIL"),
                            "Key": ("key", "KEY"),
                            "Lattice": ("lattice", "LATTICE"),
                            "Light": ("light", "LIGHT"),
                            "Mask": ("mask", "MASK"),
                            "Material": ("material", "MATERIAL"),
                            "MetaBall": ("meta", "META"),
                            "Mesh": ("mesh", "MESH"),
                            "Movie Clip": ("movieclip", "MOVIECLIP"),
                            "Node Tree": ("nodetree", "NODETREE"),
                            "Object": ("object", "OBJECT"),
                            "Light Probe": ("light_probe", "LIGHT_PROBE"),
                            "Scene": ("scene", "SCENE"),
                            "Speaker": ("speaker", "SPEAKER"),
                            "Texture": ("texture", "TEXTURE"),
                            "World": ("world", "WORLD")}
