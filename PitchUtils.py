from .i18n import i18n


def pitch_dictionary(lowest_octave: int):
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    dictionary = {}
    for i in range(0, 128):
        octave_number = int(i / 12) + lowest_octave
        note_in_octave = i % 12
        dictionary[i] = note_names[note_in_octave] + str(octave_number)
    return dictionary


C3_MIDDLE_PITCH_TO_DISPLAY = pitch_dictionary(-2)
C4_MIDDLE_PITCH_TO_DISPLAY = pitch_dictionary(-1)
C5_MIDDLE_PITCH_TO_DISPLAY = pitch_dictionary(0)

PITCHES_IN_MAJOR_SCALE = {0, 2, 4, 5, 7, 9, 11}  # pitches in a major scale (where 0 is tonic)

SCALE_TO_PITCH_MAP = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10,
                      "B": 11}


def note_display_from_pitch(pitch: int, middle_c_note: str) -> str:
    if middle_c_note == "C3":
        return C3_MIDDLE_PITCH_TO_DISPLAY[pitch]
    elif middle_c_note == "C5":
        return C5_MIDDLE_PITCH_TO_DISPLAY[pitch]
    else:
        return C4_MIDDLE_PITCH_TO_DISPLAY[pitch]


def note_description_from_pitch(pitch: int, middle_c_note: str) -> str:
    return i18n.concat(note_display_from_pitch(pitch, middle_c_note),
                       i18n.parenthetical(i18n.concat(i18n.get_text(i18n.MIDI_NOTE), str(pitch))))


def note_pitch_from_id(note_id_str: str) -> int:
    return int(note_id_str)


def note_id_is_selected_note(note_id_str: str) -> bool:
    return note_id_str == "selected"


def note_id_from_pitch(pitch: int) -> str:
    return str(pitch)


def can_be_transposed(pitch: int, steps_to_transpose: int) -> bool:
    min_note = 0 - steps_to_transpose
    max_note = 127 - steps_to_transpose
    return min_note <= pitch <= max_note


def pitch_filter_is_all_inclusive(pitch: int, comparison_operator: str) -> bool:
    return pitch == 0 and comparison_operator == "greater_than_or_equal_to" or \
        pitch == 127 and comparison_operator == "less_than_or_equal_to"


def note_in_scale(note_pitch, scale_tonic_pitch):
    return ((note_pitch - scale_tonic_pitch) % 12) in PITCHES_IN_MAJOR_SCALE
