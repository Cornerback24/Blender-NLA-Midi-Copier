from .Util import Util
import math


# contains data from the header chunk
class HeaderData:
    def __init__(self):
        self.ticks_per_beat = None
        self.frames_per_second = None
        self.ticks_per_frame = None
        self.format_type = None
        self.num_tracks = None

    def __str__(self):
        s = ("Header Chunk, Format type: " + str(self.format_type)
             + " Number of tracks: " + str(self.num_tracks))

        if self.ticks_per_beat is not None:
            s = s + "\n\t Ticks per beat: " + str(self.ticks_per_beat)

        if self.frames_per_second is not None:
            s = s + "\n\t Frames per second: " + str(self.frames_per_second)
            s = s + "\n\t Ticks per frame: " + str(self.ticks_per_frame)
        return s

    def set_from_bytes(self, header_def_bytes, header_body_bytes):
        self.format_type = int.from_bytes(header_body_bytes[0:2], "big")
        self.num_tracks = int.from_bytes(header_body_bytes[2:4], "big")
        time_division = header_body_bytes[4:6]
        if Util.msb_is_one(header_body_bytes):  # frames per second
            self.frames_per_second = time_division[0] & int('7f', 16)
            if self.frames_per_second == 29:
                self.frames_per_second = 29.97
            self.ticks_per_frame = int.from_bytes(time_division[1:2], "big")
        else:  # ticks per beat
            self.ticks_per_beat = int.from_bytes(time_division, "big")
        return


class TrackHeader:
    def __init__(self):
        # number of bytes in the chunk
        self.chunk_size = None

    def set_from_bytes(self, midi_data):
        self.chunk_size = Util.int_from_bytes(midi_data[4:])

    def __str__(self):
        return "Track Header, Chunk Size: " + str(self.chunk_size)


# parent class for all midi events with delta time information
# delta_time and all relevant data must be set on all midi events
# (if data is not set, __str__ will fail)
class MidiEvent:
    def __init__(self):
        # delta time in clock ticks
        self.delta_time = None
        # start time in ms
        self.start_time = None
        # start time in ticks
        self.start_time_ticks = None

    # set the delta time in clock ticks from the bytes representing delta time
    def set_delta_time_from_bytes(self, delta_time_bytes):
        self.delta_time = Util.var_len_val(delta_time_bytes)

    # sets the event data from the bytes (bytes should not include delta time)
    # this method is defined in every child class

    def set_from_bytes(self, midi_data_bytes):
        print("Set bytes called on parent midi event class!")

    def __str__(self):
        return ("Midi Event" + " " +
                " delta_time: " + str(self.delta_time))

    # set start time in ms
    def set_start_time_ms(self, start_time_ms):
        self.start_time = start_time_ms

    def set_start_time_ticks(self, start_time_ticks):
        self.start_time_ticks = start_time_ticks


# ---------------------- Meta Events ------------------------------
class MetaEvent(MidiEvent):
    def set_from_bytes(self, midi_data):
        print("Set bytes called on parent meta event class!")

    def __str__(self):
        return "Meta  delta_time: " + str(self.delta_time)


class SequenceNumberEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.sequence_number = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.sequence_number = int.from_bytes(event_data, "big")

    def __str__(self):
        return (super().__str__() + ", eventType: Sequence Number" +
                "\n\t Sequence Number: " + str(self.sequence_number))


class TextEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.text = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.text = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Text" +
                "\n\t Text: " + str(self.text))


class CopyrightNoticeEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.copyright_notice = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.copyright_notice = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Copyright Notice" +
                "\n\t Copyright Notice: " + str(self.copyright_notice))


class TrackNameEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.track_name = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.track_name = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Sequence/Track Name" +
                "\n\t Track Name: " + str(self.track_name))


class InstrumentNameEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.instrument_name = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.instrument_name = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Instrument Name" +
                "\n\t Instrument Name: " + str(self.instrument_name))


class LyricsEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.lyrics = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.lyrics = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Lyrics" +
                "\n\t Lyrics: " + str(self.lyrics))


class MarkerEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        # marker text
        self.marker = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.marker = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType:Marker" +
                "\n\t Marker: " + str(self.marker))


class CuePointEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        # cue point text
        self.cue_point = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.cue_point = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Cue Point" +
                "\n\t Cue Point: " + str(self.cue_point))


class ProgramNameEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.program_name = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.program_name = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Program Name" +
                "\n\t Program Name: " + str(self.program_name))


class DeviceNameEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.device_name = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.device_name = event_data.decode()

    def __str__(self):
        return (super().__str__() + ", eventType: Device Name" +
                "\n\t Device Name: " + str(self.device_name))


class MidiChannelPrefixEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.channel = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.channel = Util.int_from_bytes(event_data)

    def __str__(self):
        return (super().__str__() + ", eventType: Midi Channel Prefix"
                + "\n\t Channel: " + str(self.channel))


class MidiPortEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.port = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.port = Util.int_from_bytes(event_data)

    def __str__(self):
        return (super().__str__() + ", eventType: Midi Port"
                + "\n\t Port: " + str(self.port))


class EndOfTrackEvent(MetaEvent):
    def set_from_bytes(self, midi_data):
        # nothing to set for end of track
        return

    def __str__(self):
        return super().__str__() + ", eventType: End of Track"


class SetTempoEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        # tempo in microseconds per quarter note
        self.tempo = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        self.tempo = Util.int_from_bytes(event_data)

    def __str__(self):
        return (super().__str__() + ", eventType: Set Tempo"
                + "\n\t Tempo (microseconds per quarter note): "
                + str(self.tempo))


class SMPTEOffsetEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        # fps
        self.frame_rate = None
        self.drop_frame = False
        self.hour = None
        self.minute = None
        self.second = None
        self.frame = None
        # always 100 sub-frames per frame
        self.sub_frame = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        frame_rate_identifier = (event_data[0] & int('e0', 16)) / 64
        # frame rate in fps
        self.frame_rate = None
        self.drop_frame = False
        if frame_rate_identifier == 0:
            self.frame_rate = 24
        if frame_rate_identifier == 1:
            self.frame_rate = 25
        if frame_rate_identifier == 10:
            self.frame_rate = 29.97
            self.drop_frame = True
        if frame_rate_identifier == 11:
            self.frame_rate = 30
        self.hour = event_data[0] & int('1f', 16)
        self.minute = Util.int_from_bytes(event_data[1:2])
        self.second = Util.int_from_bytes(event_data[2:3])
        self.frame = Util.int_from_bytes(event_data[3:4])
        # always 100 sub-frames per frame
        self.sub_frame = Util.int_from_bytes(event_data[4:])

    def __str__(self):
        return (super().__str__() + ", eventType: SMPTE Offset"
                + "\n\t Frame Rate: " + str(self.frame_rate)
                + ", Drop Frame: " + str(self.drop_frame)
                + "\n\t Hour: " + str(self.hour)
                + ", Minute: " + str(self.minute)
                + "\n\t Frame: " + str(self.frame)
                + ", Sub-Frame: " + str(self.sub_frame))


class TimeSignatureEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        self.numerator = None
        # actual time signature denominator
        self.denominator = None
        self.beats_per_tick = None
        self.thirty_second_notes_per_beat = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        # default is 4
        self.numerator = Util.int_from_bytes(event_data[0:1])
        # default is 4 (or encoded 2 since 2^2 is 4)
        self.denominator = math.pow(2, Util.int_from_bytes(event_data[1:2]))
        # default is 1 (or 24 encoded since 24/24 = 1)
        self.beats_per_tick = Util.int_from_bytes(event_data[2:3]) / 24
        # default is 8
        self.thirty_second_notes_per_beat = Util.int_from_bytes(event_data[3:])

    def __str__(self):
        return (super().__str__() + ", eventType: Time Signature"
                + "\n\t Time Signature: " + str(self.numerator)
                + "/" + str(self.denominator)
                + "\n\t Beats per tick: " + str(self.beats_per_tick)
                + ", 32nd notes per beat: " + str(self.thirty_second_notes_per_beat))


class KeySignatureEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        # True for major, false for minor
        self.major_key = None
        # True if sharp key, false if flat key (should be disregarded if number of accidentals is zero)
        self.sharp_key = None
        self.number_of_accidentals = None

    def set_from_bytes(self, midi_data):
        event_data = Util.strip_leading_variable_length(midi_data[2:])
        # True for major, False for minor
        self.major_key = (Util.int_from_bytes(event_data[1:2]) == 0)
        # true for sharps, false for flats
        self.sharp_key = (Util.int_from_bytes(event_data[0:1], True) > 0)
        self.number_of_accidentals = abs(Util.int_from_bytes(event_data[0:1], True))

    def __str__(self):
        sharps_or_flats = "sharps" if self.sharp_key else "flats"
        major_or_minor = ""
        if self.number_of_accidentals > 0:
            major_or_minor = ", major" if self.major_key else ", minor"
        return (super().__str__() + ", eventType: Key Signature"
                + "\n\t Number of " + str(sharps_or_flats) + ": "
                + str(self.number_of_accidentals) + major_or_minor)


class SequencerSpecificEvent(MetaEvent):
    def __init__(self):
        super().__init__()
        # raw event data without the variable-length length property
        self.event_data = None

    def set_from_bytes(self, midi_data):
        self.event_data = Util.strip_leading_variable_length(midi_data[2:])

    def __str__(self):
        return (super().__str__() + ", eventType: Sequencer Specific"
                + "\n\t Raw data (without variable-length)" + str(self.event_data))


# --------------------------------- System Exclusive Events ------------------------------
class SystemExclusiveEvent(MidiEvent):
    def __init__(self):
        super().__init__()
        # raw event data without the variable-length length property
        self.event_data = None

    def set_from_bytes(self, midi_data):
        self.event_data = Util.strip_leading_variable_length(midi_data[1:])

    def __str__(self):
        return ("System " + " delta_time: " + str(self.delta_time)
                + "\n\t Raw data (without variable-length)" + str(self.event_data))


# --------------------------------- Channel Events -------------------------------------
class ChannelEvent(MidiEvent):
    # when calling this on a child class, midi_data should have a status byte
    def set_from_bytes(self, midi_data):
        print("Set bytes called on parent channel event class!")

    def __str__(self):
        return "Channel  delta_time: " + str(self.delta_time)


class NoteOffEvent(ChannelEvent):
    def __init__(self):
        super().__init__()
        self.channel = None
        self.note_number = None
        self.release_velocity = None

    def set_from_bytes(self, midi_data):
        self.channel = midi_data[0] & int('0f', 16)
        self.note_number = midi_data[1]
        self.release_velocity = midi_data[2]

    def __str__(self):
        return (super().__str__() + ", eventType: Note Off"
                + ", Channel: " + str(self.channel)
                + "\n\t Note Number: " + str(self.note_number)
                + ", Velocity: " + str(self.release_velocity))


class NoteOnEvent(ChannelEvent):
    def __init__(self):
        super().__init__()
        self.channel = None
        self.note_number = None
        self.velocity = None

    def set_from_bytes(self, midi_data):
        self.channel = midi_data[0] & int('0f', 16)
        self.note_number = midi_data[1]
        self.velocity = midi_data[2]

    # note on with velocity zero is really note off
    def is_note_off(self):
        return self.velocity == 0

    def __str__(self):
        event_type = ("Note Off (as Note On)" if self.is_note_off()
                      else "Note On")
        return (super().__str__() + ", event_type: " + event_type
                + ", Channel: " + str(self.channel)
                + "\n\t Note Number: " + str(self.note_number)
                + ", Velocity: " + str(self.velocity))


class NoteAftertouchEvent(ChannelEvent):
    def __init__(self):
        super().__init__()
        self.channel = None
        self.note_number = None
        self.aftertouch_amount = None

    def set_from_bytes(self, midi_data):
        self.channel = midi_data[0] & int('0f', 16)
        self.note_number = midi_data[1]
        self.aftertouch_amount = midi_data[2]

    def __str__(self):
        return (super().__str__() + ", eventType: Note Aftertouch"
                + ", Channel: " + str(self.channel)
                + "\n\t Note Number: " + str(self.note_number)
                + " Aftertouch: " + str(self.aftertouch_amount))


class ControllerEvent(ChannelEvent):
    def __init__(self):
        super().__init__()
        self.channel = None
        # string mapping to this number can be found with Util.controller_string
        self.controller_type = None
        self.value = None

    def set_from_bytes(self, midi_data):
        self.channel = midi_data[0] & int('0f', 16)
        self.controller_type = midi_data[1]
        self.value = midi_data[2]

    def controller_type_string(self):
        controller_string = Util.controller_string(self.controller_type)
        return controller_string if controller_string is not None else str(self.controller_type)

    def __str__(self):
        return (super().__str__() + ", eventType: Controller"
                + ", Channel: " + str(self.channel)
                + "\n\t Controller Type: " + str(self.controller_type_string())
                + ", Value: " + str(self.value))


class ProgramChangeEvent(ChannelEvent):
    def __init__(self):
        super().__init__()
        self.channel = None
        self.program_number = None

    def set_from_bytes(self, midi_data):
        self.channel = midi_data[0] & int('0f', 16)
        self.program_number = midi_data[1]

    def __str__(self):
        return (super().__str__() + ", eventType: Program Change"
                + ", Channel: " + str(self.channel)
                + "\n\t Program Number: " + str(self.program_number))


class ChannelAftertouchEvent(ChannelEvent):
    def __init__(self):
        super().__init__()
        self.channel = None
        self.aftertouch_amount = None

    def set_from_bytes(self, midi_data):
        self.channel = midi_data[0] & int('0f', 16)
        self.aftertouch_amount = midi_data[1]

    def __str__(self):
        return (super().__str__() + ", eventType: Channel Aftertouch"
                + ", Channel: " + str(self.channel)
                + "\n\t Aftertouch: " + str(self.aftertouch_amount))


class PitchBendEvent(ChannelEvent):
    def __init__(self):
        super().__init__()
        self.channel = None
        self.bend_amount = None

    def set_from_bytes(self, midi_data):
        self.channel = midi_data[0] & int('0f', 16)
        # NOTE: this relies on Util.var_len_val not actually caring if
        # the format is an actual valid variable length value
        # (and thus completely ignoring the msb of every byte)
        self.bend_amount = Util.var_len_val(midi_data[2:3] + midi_data[1:2])

    # pitchValue relative to 8192; positive for increase, negative for decrease
    def relative_bend_amount(self):
        return self.bend_amount - 8192

    def __str__(self):
        return (super().__str__() + ", eventType: Pitch Bend"
                + ", Channel: " + str(self.channel)
                + "\n\t Amount (relative to 8192): "
                + str(self.relative_bend_amount()))


class EventDictionaries:
    # maps a meta event type to its class
    META_EVENT_DICTIONARY = MetaEventDict = {0: SequenceNumberEvent,
                                             1: TextEvent,
                                             2: CopyrightNoticeEvent,
                                             3: TrackNameEvent,
                                             4: InstrumentNameEvent,
                                             5: LyricsEvent,
                                             6: MarkerEvent,
                                             7: CuePointEvent,
                                             8: ProgramNameEvent,
                                             9: DeviceNameEvent,
                                             32: MidiChannelPrefixEvent,
                                             33: MidiPortEvent,
                                             47: EndOfTrackEvent,
                                             81: SetTempoEvent,
                                             84: SMPTEOffsetEvent,
                                             88: TimeSignatureEvent,
                                             89: KeySignatureEvent,
                                             127: SequencerSpecificEvent}
    # maps [byte with event type and channel] & b'\xf0' to event type
    CHANNEL_EVENT_DICTIONARY = {int('80', 16): NoteOffEvent,
                                int('90', 16): NoteOnEvent,
                                int('a0', 16): NoteAftertouchEvent,
                                int('b0', 16): ControllerEvent,
                                int('c0', 16): ProgramChangeEvent,
                                int('d0', 16): ChannelAftertouchEvent,
                                int('e0', 16): PitchBendEvent}
