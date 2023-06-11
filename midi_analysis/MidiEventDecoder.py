from .MidiParser import MidiParser
from .MidiEvents import *
from .Util import Util


# decodes data from the MidiParser into data easier to work with in MidiData
# (will decode each piece of data from midi_parser into an event,
# including header chunk pieces)
class MidiEventDecoder:
    def __init__(self, midi_filename):
        self.midi_parser = MidiParser(midi_filename)
        self.running_status = False
        self.last_channel_status_byte = None  # the first byte of the last channel event that didn't use running status
        return

    def has_more_events(self):
        return self.midi_parser.has_more_data()

    # be sure to call this once before calling next_event
    def header_data(self):
        data = HeaderData()
        data.set_from_bytes(self.midi_parser.read_next_data(),
                            self.midi_parser.read_next_data())
        return data

    # returns a MidiEvent
    def next_event(self):
        return self.midi_event(self.midi_parser.read_next_data())
    # creates a MidiEvent from the midi_data

    def midi_event(self, midi_data):
        # check if TrackHeader
        if midi_data[0:4] == b'MTrk':
            track_header = TrackHeader()
            track_header.set_from_bytes(midi_data)
            return track_header
        # find delta_time
        temp_data = midi_data
        delta_time_bytes_length = 0
        while Util.msb_is_one(temp_data[delta_time_bytes_length:]):
            delta_time_bytes_length += 1
        delta_time_bytes_length += 1
        delta_time = temp_data[:delta_time_bytes_length]
        midi_data = temp_data[delta_time_bytes_length:]
        # Meta Event
        if midi_data[0:1] == b'\xff':
            if midi_data[1] in EventDictionaries.META_EVENT_DICTIONARY:
                meta_event_class = EventDictionaries.META_EVENT_DICTIONARY[midi_data[1]]
            else:
                meta_event_class = MetaEvent
            meta_event = meta_event_class()
            meta_event.set_delta_time_from_bytes(delta_time)
            meta_event.set_from_bytes(midi_data)
            return meta_event
        # System Event
        if midi_data[0:1] == b'\xf0' or midi_data[0:1] == b'\xf7':
            system_event = SystemExclusiveEvent()
            system_event.set_delta_time_from_bytes(delta_time)
            system_event.set_from_bytes(midi_data)
            return system_event
        # Channel Event
        if Util.msb_is_one(midi_data):  # running status
            self.last_channel_status_byte = midi_data[0:1]
        else:  # not running status
            midi_data = self.last_channel_status_byte + midi_data
        channel_event_identifier = midi_data[0] & int('f0', 16)
        if channel_event_identifier in EventDictionaries.CHANNEL_EVENT_DICTIONARY:
            channel_event_class = EventDictionaries.CHANNEL_EVENT_DICTIONARY[channel_event_identifier]
        else:
            channel_event_class = ChannelEvent
        channel_event = channel_event_class()
        channel_event.set_delta_time_from_bytes(delta_time)
        channel_event.set_from_bytes(midi_data)
        return channel_event

    def close(self):
        self.midi_parser.close()
