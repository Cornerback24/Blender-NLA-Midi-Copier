from .midi_analysis.Note import Note


def pitch_dictionary(lowest_octave: int):
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    dictionary = {}
    for i in range(0, 128):
        octave_number = int(i / 12) + lowest_octave
        note_in_octave = i % 12
        dictionary[i] = note_names[note_in_octave] + str(octave_number)
    return dictionary


NOTE_ID_TO_PITCH = {v: k for k, v in Note.PITCH_DICTIONARY.items()}

C3_MIDDLE_PITCH_TO_DISPLAY = pitch_dictionary(-2)
C4_MIDDLE_PITCH_TO_DISPLAY = pitch_dictionary(-1)
C5_MIDDLE_PITCH_TO_DISPLAY = pitch_dictionary(0)


def note_display_from_pitch(pitch: int, middle_c_note: str) -> str:
    if middle_c_note == "C3":
        return C3_MIDDLE_PITCH_TO_DISPLAY[pitch]
    elif middle_c_note == "C5":
        return C5_MIDDLE_PITCH_TO_DISPLAY[pitch]
    else:
        return C4_MIDDLE_PITCH_TO_DISPLAY[pitch]


def note_description_from_pitch(pitch: int, middle_c_note: str) -> str:
    return f"{note_display_from_pitch(pitch, middle_c_note)} (Midi note {pitch})"


def note_display_from_id(note_id_str: str, middle_c_note: str) -> str:
    return note_display_from_pitch(NOTE_ID_TO_PITCH[note_id_str], middle_c_note)


def note_pitch_from_id(note_id_str: str) -> int:
    return NOTE_ID_TO_PITCH[note_id_str]


def note_id_from_pitch(pitch: int) -> str:
    return Note.PITCH_DICTIONARY[pitch]


def can_be_transposed(pitch: int, steps_to_transpose: int) -> bool:
    min_note = 0 - steps_to_transpose
    max_note = 127 - steps_to_transpose
    return min_note <= pitch <= max_note


def pitch_filter_is_all_inclusive(pitch: int, comparison_operator: str) -> bool:
    return pitch == 0 and comparison_operator == "greater_than_or_equal_to" or \
           pitch == 127 and comparison_operator == "less_than_or_equal_to"
