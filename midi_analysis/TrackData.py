from .Note import Note
from .MidiEvents import *
import bisect


# contains data for a single track
class TrackData:
    def __init__(self, name="", middle_c="C4"):
        self.notes = []
        # maps pitches to notes without end times
        self.incomplete_notes = {}
        # for handling a note on followed by a note off at the same time
        # note on - - - note on, note off - - - note off treated as two notes:
        # first note on to first note off, second note on to second note off
        self.skipped_note_on_events = {}
        self.events = []
        self.name = name
        self.delta_time_total = 0
        # if false, time division is frames per second
        self.is_ticks_per_beat = True
        self.debug = False
        self.middle_c = middle_c
        return

    def note_from_note_on_event(self, note_on_event):
        return Note(note_on_event.start_time,
                    note_on_event.start_time_ticks,
                    note_on_event.note_number,
                    note_on_event.velocity,
                    note_on_event.channel,
                    self.middle_c)

    # Events need to be added in order, last event must be end of track
    def add_event(self, event):
        self.events.append(event)
        if isinstance(event, TrackNameEvent):
            self.name = event.track_name
        elif (isinstance(event, NoteOnEvent) and
              not (event.is_note_off())):
            if event.note_number in self.incomplete_notes:
                self.skipped_note_on_events[event.note_number] = self.note_from_note_on_event(event)
                # note will be skipped unless there is a note off event at the same time
                if self.debug:
                    print("Note on event for note " + str(event.note_number)
                          + " already playing, potentially skipping...")
            else:
                self.incomplete_notes[event.note_number] = self.note_from_note_on_event(event)
        elif (isinstance(event, NoteOffEvent) or
              (isinstance(event, NoteOnEvent) and event.is_note_off())):
            if event.note_number in self.incomplete_notes:
                self.incomplete_notes[event.note_number].set_end_time(event.start_time)
                self.incomplete_notes[event.note_number].set_end_time_ticks(event.start_time_ticks)
                self.notes.append(self.incomplete_notes[event.note_number])
                del self.incomplete_notes[event.note_number]

                # check if there was a note on event for the next note at the same time in case it was listed before
                # this note off event
                if event.note_number in self.skipped_note_on_events:
                    skipped_note = self.skipped_note_on_events[event.note_number]
                    if skipped_note.start_time == event.start_time:
                        # add the note back so it can be completed by the next note off
                        if self.debug:
                            print("Note off at same time as note on for " + str(event.note_number) +
                                  ". Un-skipping note-on event")
                        self.incomplete_notes[event.note_number] = skipped_note
            elif self.debug:
                print("Note off event for note " + str(event.note_number)
                      + " not playing, skipping...")
        elif isinstance(event, EndOfTrackEvent):
            self.notes.sort()


# this is kind of like an ordered dictionary
class TempoChanges:
    def __init__(self):
        self.tempo_changes = []
        self.index = 0
        return

    # tempo changes need to be added in order
    # tempo in microseconds per quarter note
    # may change the index and affect which TempoChange is marked as next
    # All tempo changes should be defined in track 0 of a type one midi file
    # (or at least before any notes, FL Studio seems to put tempo changes in track 1...)
    # so the possible index change shouldn't be an issue for MidiData
    def add_tempo_change(self, delta_time_total, tempo):
        bisect.insort(self.tempo_changes,
                      TempoChange(delta_time_total, tempo))

    # so that class can be used as a stream
    def delta_time_total(self):
        return self.tempo_changes[self.index].delta_time_total

    def us_per_quarter(self):
        return self.tempo_changes[self.index].tempo

    def find_next(self):
        self.index += 1

    # returns true if the current index is a tempo change
    # (will return true if find_next will go beyond end of
    # list, this is intentional)
    def has_more(self):
        return self.index < len(self.tempo_changes)

    def reset(self):  # go back to first tempo change
        self.index = 0


class TempoChange:
    # delta_time_total in ticks
    # tempo in microseconds per quarter note
    def __init__(self, delta_time_total, tempo):
        self.delta_time_total = delta_time_total
        self.tempo = tempo

    def __lt__(self, other):
        return self.delta_time_total < other.delta_time_total
