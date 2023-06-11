class Note:
    # start and end times are in ms
    def __init__(self, start, start_ticks, pitch, velocity, channel, middle_c="C4"):
        self.pitch = pitch  # note number
        self.channel = channel
        self.start_time = start
        self.end_time = None
        self.start_time_ticks = start_ticks
        self.end_time_ticks = None
        self.velocity = velocity
        self.release_velocity = None
        self.middle_c = middle_c
        return

    def set_end_time(self, end_time):
        self.end_time = end_time

    def set_end_time_ticks(self, end_time_ticks):
        self.end_time_ticks = end_time_ticks

    def set_release_velocity(self, release_velocity):
        self.release_velocity = release_velocity

    def length(self):
        return self.end_time - self.start_time

    # returns a value used in sorting the notes
    # notes are sorted by time, pitch

    def sort_val(self):
        return (self.start_time + 1) * 1000 + self.pitch * .001

    def __lt__(self, other):
        return self.sort_val() < other.sort_val()

    def __str__(self):
        pitches = Note.PITCH_DICTIONARY_C3 if self.middle_c == "C3" else \
            (Note.PITCH_DICTIONARY_C5 if self.middle_c == "C5" else Note.PITCH_DICTIONARY_C4)
        if self.pitch in pitches:
            pitch = pitches[self.pitch]
        else:
            pitch = str(self.pitch)
        return ("Note " + str(pitch) + " "
                + str("{0:.2f}".format(round(self.start_time * .001, 2))) + "s to "
                + str("{0:.2f}".format(round(self.end_time * .001, 2))) + "s"
                + " Channel: " + str(self.channel))

    # Middle C (pitch 60) = C3
    PITCH_DICTIONARY_C3 = {0: "C-2", 1: "C#-2", 2: "D-2", 3: "D#-2", 4: "E-2", 5: "F-2", 6: "F#-2", 7: "G-2", 8: "G#-2",
                           9: "A-2", 10: "A#-2", 11: "B-2", 12: "C-1", 13: "C#-1", 14: "D-1", 15: "D#-1", 16: "E-1",
                           17: "F-1", 18: "F#-1", 19: "G-1", 20: "G#-1", 21: "A-1", 22: "A#-1", 23: "B-1", 24: "C0",
                           25: "C#0", 26: "D0", 27: "D#0", 28: "E0", 29: "F0", 30: "F#0", 31: "G0", 32: "G#0", 33: "A0",
                           34: "A#0", 35: "B0", 36: "C1", 37: "C#1", 38: "D1", 39: "D#1", 40: "E1", 41: "F1", 42: "F#1",
                           43: "G1", 44: "G#1", 45: "A1", 46: "A#1", 47: "B1", 48: "C2", 49: "C#2", 50: "D2", 51: "D#2",
                           52: "E2", 53: "F2", 54: "F#2", 55: "G2", 56: "G#2", 57: "A2", 58: "A#2", 59: "B2", 60: "C3",
                           61: "C#3", 62: "D3", 63: "D#3", 64: "E3", 65: "F3", 66: "F#3", 67: "G3", 68: "G#3", 69: "A3",
                           70: "A#3", 71: "B3", 72: "C4", 73: "C#4", 74: "D4", 75: "D#4", 76: "E4", 77: "F4", 78: "F#4",
                           79: "G4", 80: "G#4", 81: "A4", 82: "A#4", 83: "B4", 84: "C5", 85: "C#5", 86: "D5", 87: "D#5",
                           88: "E5", 89: "F5", 90: "F#5", 91: "G5", 92: "G#5", 93: "A5", 94: "A#5", 95: "B5", 96: "C6",
                           97: "C#6", 98: "D6", 99: "D#6", 100: "E6", 101: "F6", 102: "F#6", 103: "G6", 104: "G#6",
                           105: "A6", 106: "A#6", 107: "B6", 108: "C7", 109: "C#7", 110: "D7", 111: "D#7", 112: "E7",
                           113: "F7", 114: "F#7", 115: "G7", 116: "G#7", 117: "A7", 118: "A#7", 119: "B7", 120: "C8",
                           121: "C#8", 122: "D8", 123: "D#8", 124: "E8", 125: "F8", 126: "F#8", 127: "G8"}

    # Middle C (pitch 60) = C4
    PITCH_DICTIONARY_C4 = {0: "C-1", 1: "C#-1", 2: "D-1", 3: "D#-1", 4: "E-1", 5: "F-1", 6: "F#-1",
                           7: "G-1", 8: "G#-1", 9: "A-1", 10: "A#-1", 11: "B-1", 12: "C0", 13: "C#0",
                           14: "D0", 15: "D#0", 16: "E0", 17: "F0", 18: "F#0", 19: "G0",
                           20: "G#0", 21: "A0", 22: "A#0", 23: "B0", 24: "C1", 25: "C#1", 26: "D1",
                           27: "D#1", 28: "E1", 29: "F1", 30: "F#1", 31: "G1", 32: "G#1", 33: "A1", 34: "A#1",
                           35: "B1", 36: "C2", 37: "C#2", 38: "D2", 39: "D#2", 40: "E2", 41: "F2",
                           42: "F#2", 43: "G2", 44: "G#2", 45: "A2", 46: "A#2", 47: "B2", 48: "C3",
                           49: "C#3", 50: "D3", 51: "D#3", 52: "E3", 53: "F3", 54: "F#3", 55: "G3",
                           56: "G#3", 57: "A3", 58: "A#3", 59: "B3", 60: "C4", 61: "C#4", 62: "D4",
                           63: "D#4", 64: "E4", 65: "F4", 66: "F#4", 67: "G4", 68: "G#4", 69: "A4",
                           70: "A#4", 71: "B4", 72: "C5", 73: "C#5", 74: "D5", 75: "D#5", 76: "E5",
                           77: "F5", 78: "F#5", 79: "G5", 80: "G#5", 81: "A5", 82: "A#5", 83: "B5",
                           84: "C6", 85: "C#6", 86: "D6", 87: "D#6", 88: "E6", 89: "F6", 90: "F#6",
                           91: "G6", 92: "G#6", 93: "A6", 94: "A#6", 95: "B6", 96: "C7", 97: "C#7",
                           98: "D7", 99: "D#7", 100: "E7", 101: "F7", 102: "F#7", 103: "G7", 104: "G#7",
                           105: "A7", 106: "A#7", 107: "B7", 108: "C8", 109: "C#8", 110: "D8",
                           111: "D#8", 112: "E8", 113: "F8", 114: "F#8", 115: "G8", 116: "G#8",
                           117: "A8", 118: "A#8", 119: "B8", 120: "C9", 121: "C#9", 122: "D9",
                           123: "D#9", 124: "E9", 125: "F9", 126: "F#9", 127: "G9"}

    # Middle C (pitch 60) = C5
    PITCH_DICTIONARY_C5 = {0: "C0", 1: "C#0", 2: "D0", 3: "D#0", 4: "E0", 5: "F0", 6: "F#0",
                           7: "G0", 8: "G#0", 9: "A0", 10: "A#0", 11: "B0", 12: "C1", 13: "C#1",
                           14: "D1", 15: "D#1", 16: "E1", 17: "F1", 18: "F#1", 19: "G1",
                           20: "G#1", 21: "A1", 22: "A#1", 23: "B1", 24: "C2", 25: "C#2", 26: "D2",
                           27: "D#2", 28: "E2", 29: "F2", 30: "F#2", 31: "G2", 32: "G#2", 33: "A2", 34: "A#2",
                           35: "B2", 36: "C3", 37: "C#3", 38: "D3", 39: "D#3", 40: "E3", 41: "F3",
                           42: "F#3", 43: "G3", 44: "G#3", 45: "A3", 46: "A#3", 47: "B3", 48: "C4",
                           49: "C#4", 50: "D4", 51: "D#4", 52: "E4", 53: "F4", 54: "F#4", 55: "G4",
                           56: "G#4", 57: "A4", 58: "A#4", 59: "B4", 60: "C5", 61: "C#5", 62: "D5",
                           63: "D#5", 64: "E5", 65: "F5", 66: "F#5", 67: "G5", 68: "G#5", 69: "A5",
                           70: "A#5", 71: "B5", 72: "C6", 73: "C#6", 74: "D6", 75: "D#6", 76: "E6",
                           77: "F6", 78: "F#6", 79: "G6", 80: "G#6", 81: "A6", 82: "A#6", 83: "B6",
                           84: "C7", 85: "C#7", 86: "D7", 87: "D#7", 88: "E7", 89: "F7", 90: "F#7",
                           91: "G7", 92: "G#7", 93: "A7", 94: "A#7", 95: "B7", 96: "C8", 97: "C#8",
                           98: "D8", 99: "D#8", 100: "E8", 101: "F8", 102: "F#8", 103: "G8", 104: "G#8",
                           105: "A8", 106: "A#8", 107: "B8", 108: "C9", 109: "C#9", 110: "D9",
                           111: "D#9", 112: "E9", 113: "F9", 114: "F#9", 115: "G9", 116: "G#9",
                           117: "A9", 118: "A#9", 119: "B9", 120: "C10", 121: "C#10", 122: "D10",
                           123: "D#10", 124: "E10", 125: "F10", 126: "F#10", 127: "G10"}

    # For backwards compatibility
    PITCH_DICTIONARY = PITCH_DICTIONARY_C4
