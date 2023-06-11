# returns elements of a midi file (in raw form as a bytes object)
# elements returned:
#   Chuck ID along with chunk size
#   The rest of the header chunk
#   Midi Channel events, including delta time
#   Meta Event
#   System Exclusive Event
from .Util import Util


class MidiParser:
    # states, CHUCK_START means start of either header or track
    CHUNK_START, IN_HEADER, IN_TRACK_CHUNK,  = range(3)

    def __init__(self, midi_filename):
        self.midi_file = open(midi_filename, "rb")
        self.bytes_left_in_chunk = 0
        self.next_byte = self.midi_file.read(1)
        self.state = self.CHUNK_START
        self.NO_SECOND_PARAM_EVENTS = [
            int('c0', 16),  # program change
            int('d0', 16),  # channel pressure (aftertouch)
        ]
        return

    def has_more_data(self):
        return self.next_byte != b''

    # true if the current chunk has more bytes (false if a read would be
    # end of file or the next chuck (header chuck or track chunk).
    def chunk_has_more_data(self):
        return self.bytes_left_in_chunk > 0

    # returns the data of the next element in bytes
    def read_next_data(self):
        if self.next_byte == b'':
            print("Tried to read end of file!")
            return self.next_byte
        if self.state == self.CHUNK_START:  # return ID along with chunk size
            return_val = self.read_next_bytes(8)
            if return_val[0:4] == b'MThd':
                self.state = self.IN_HEADER
            if return_val[0:4] == b'MTrk':
                self.state = self.IN_TRACK_CHUNK
            self.bytes_left_in_chunk = int.from_bytes(return_val[4:8], "big")
            return return_val
        if self.state == self.IN_HEADER:  # return body of header
            return self.read_next_bytes(self.bytes_left_in_chunk)
        if self.state == self.IN_TRACK_CHUNK:  # return an event
            return self.read_event()
        raise MidiParserException("Midi parser state " + str(self.state) + " not recognized")

    def read_event(self):
        delta_time = self.read_variable_length()
        first_byte = self.read_next_byte()
        if first_byte == b'\xff':
            return delta_time + self.read_meta_event(first_byte)
        elif first_byte == b'\xf0' or first_byte == b'\xf7':
            return delta_time + self.read_sys_ex_event(first_byte)
        else:
            return delta_time + self.read_channel_event(first_byte)

    def read_channel_event(self, first_byte):
        data_length = 1
        if Util.msb_is_one(first_byte):  # not running status
            data_length = 2
        # program change and channel aftertouch do not have second parameter
        if (first_byte[0] & int('f0', 16)) in self.NO_SECOND_PARAM_EVENTS:
            data_length = 1
        return first_byte + self.read_next_bytes(data_length)

    def read_meta_event(self, first_byte):
        meta_event_type = self.read_next_byte()
        meta_event_length = self.read_variable_length()
        meta_event_data = self.read_next_bytes(Util.var_len_val(
            meta_event_length))
        return (first_byte + meta_event_type +
                meta_event_length + meta_event_data)

    def read_sys_ex_event(self, first_byte):
        data_length = self.read_variable_length()
        return (first_byte + data_length +
                self.read_next_bytes(Util.var_len_val(data_length)))

    def read_next_byte(self):
        if self.bytes_left_in_chunk > -0:
            self.bytes_left_in_chunk -= 1
        elif self.state == self.IN_TRACK_CHUNK:
            raise MidiParserException("More bytes in chunk than defined in chunk header")
        if self.bytes_left_in_chunk == 0:
            self.state = self.CHUNK_START
        return_val = self.next_byte
        self.next_byte = self.midi_file.read(1)
        return return_val

    def read_next_bytes(self, num_bytes):
        return_bytes = b''
        for i in range(num_bytes):
            return_bytes = return_bytes + self.read_next_byte()
        return return_bytes

    def read_variable_length(self):
        cur_byte = self.read_next_byte()
        return_val = cur_byte
        while Util.msb_is_one(cur_byte):
            cur_byte = self.read_next_byte()
            return_val = return_val + cur_byte
        return return_val

    def close(self):
        self.midi_file.close()


class MidiParserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
