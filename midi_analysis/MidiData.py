from .MidiEventDecoder import MidiEventDecoder
from .TrackData import TrackData
from .TrackData import TempoChanges
from .MidiEvents import *


# contains the finalized data after analysis
class MidiData:
    def __init__(self, midi_filename, middle_c="C4"):
        self.event_decoder = MidiEventDecoder(midi_filename)
        header_data = self.event_decoder.header_data()
        # variables
        self.format = header_data.format_type
        self.num_tracks = header_data.num_tracks
        self.is_ticks_per_beat = False
        self.middle_c = middle_c
        if header_data.ticks_per_beat is None:
            self.is_ticks_per_beat = False
            self.ticks_per_second = (header_data.frames_per_second *
                                     header_data.ticks_per_frame)
        else:
            self.is_ticks_per_beat = True
            self.ticks_per_beat = header_data.ticks_per_beat

        if header_data.format_type != 1 and header_data.format_type != 0:
            raise NotSupportedException("Midi files of format " + str(header_data.format_type)
                                        + " are not supported")

        # maps running total of delta times to microsecondsPerQuarter
        tempo_changes = TempoChanges()
        self.tracks = []

        self.ms_per_beat = 500  # default 120 bpm

        # read in each track
        tracknum = 0  # used to create temporary track names
        while self.event_decoder.has_more_events():
            track_name = "Track" + str(tracknum)
            tracknum += 1
            track_data = TrackData(name=track_name, middle_c=self.middle_c)
            # should be a track header
            event = self.event_decoder.next_event()
            if not (isinstance(event, TrackHeader)):
                raise UnexpectedEventException(event, TrackHeader())
            # set up tempo_changes
            tempo_changes.reset()
            self.ms_per_beat = 500  # default 120 bpm
            delta_time_total = 0  # current time in ticks
            ms_total = 0  # current time in ms
            # add events
            while not (isinstance(event, EndOfTrackEvent)):
                event = self.event_decoder.next_event()
                next_total = delta_time_total + event.delta_time
                # calculate absolute start time for event in ms
                if self.is_ticks_per_beat:
                    while (tempo_changes.has_more() and
                           next_total >= tempo_changes.delta_time_total()):
                        ms_total += ((tempo_changes.delta_time_total() - delta_time_total) * self.ms_per_beat / self.ticks_per_beat)
                        delta_time_total = tempo_changes.delta_time_total()
                        self.ms_per_beat = tempo_changes.us_per_quarter() * .001
                        tempo_changes.find_next()
                    ms_total += ((next_total - delta_time_total) * self.ms_per_beat / self.ticks_per_beat)
                else:
                    ms_total = (event.delta_time / self.ticks_per_second) * .001
                # add event to track_data
                delta_time_total = next_total
                if isinstance(event, SetTempoEvent):
                    tempo_changes.add_tempo_change(delta_time_total, event.tempo)
                event.set_start_time_ms(ms_total)
                event.set_start_time_ticks(delta_time_total)
                track_data.add_event(event)
            self.tracks.append(track_data)

    def get_num_tracks(self):
        return len(self.tracks)

    def get_track(self, index):
        return self.tracks[index]


class UnexpectedEventException(Exception):
    def __init__(self, event, expected_event):
        self.event = event
        self.expected_event = expected_event

    def __str__(self):
        return str("MidiData expected event of type " + str(type(self.expected_event))
                   + ", got event of type " + str(type(self.event)))


class NotSupportedException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
