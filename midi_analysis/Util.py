class Util:
    # returns a hex value for use in bytes.fromhex
    @staticmethod
    def padded_hex(source_num):
        return_val = hex(source_num)[2:]
        if (len(return_val) % 2) != 0:
            return_val = '0' + return_val
        return return_val

    # returns a bytes object shifted left by num_bits bits
    @staticmethod
    def lshift_bytes(source_bytes, num_bits):
        return bytes.fromhex(Util.padded_hex(
            int.from_bytes(source_bytes, "big") << num_bits))

    # returns a byte array shifted left by num_bits bits
    @staticmethod
    def lshift_byte_array(source_byte_array, num_bits):
        return bytearray.fromhex(Util.padded_hex(
            int.from_bytes(source_byte_array, "big") << num_bits))

    # takes a bytes object formatted in variable length and
    # returns the int value represented
    # does not check if the variable length value is valid, as
    # it ignores the msb of every byte
    @staticmethod
    def var_len_val(var_len_bytes):
        if len(var_len_bytes) == 0:
            return 0
        var_len_array = bytearray(var_len_bytes)
        return_val_bytes = bytearray.fromhex(
            Util.padded_hex(var_len_array[0] & b'\x7f'[0]))
        for i in range(len(var_len_bytes) - 1):
            next_byte = var_len_array[i + 1] & b'\x7f'[0]
            return_val_bytes = Util.lshift_byte_array(return_val_bytes, 7)
            return_val_bytes[len(return_val_bytes) - 1] = (
                    return_val_bytes[len(return_val_bytes) - 1] | next_byte)
        return int.from_bytes(return_val_bytes, "big")

    @staticmethod
    def msb_is_one(byte):  # returns true if the msb of a bytes object is 1
        return (byte[0] & int('80', 16)) > 0

    # strips a variable length quantity off of a byte array
    # and returns the rest
    @staticmethod
    def strip_leading_variable_length(byte_array):
        var_len_end_index = 0
        while (var_len_end_index < len(byte_array) and
               Util.msb_is_one(byte_array[var_len_end_index:var_len_end_index + 1])):
            var_len_end_index += 1
        # the last byte of a variable length value has msb 0
        var_len_end_index += 1
        return byte_array[var_len_end_index:]

    @staticmethod
    def int_from_bytes(byte_array, signed=False):
        return int.from_bytes(byte_array, "big", signed=signed)

    # returns None if no controller Number Mapped
    @staticmethod
    def controller_string(controller_number):
        if controller_number in Util.CONTROLLER_DICTIONARY:
            return Util.CONTROLLER_DICTIONARY[controller_number]
        elif 16 <= controller_number <= 19:
            return "General Purpose Controller " + str(controller_number - 15)
        elif 32 <= controller_number <= 63:
            controller_reference_string = Util.controller_string(controller_number - 32)
            if controller_reference_string is None:
                return None
            return "LSB for " + controller_reference_string
        elif 75 <= controller_number <= 79:
            return "Sound Controller " + str(controller_number - 74)
        elif 80 <= controller_number <= 83:
            return "General Purpose Controller " + str(controller_number - 79)
        return None

    # maps [byte with event type and channel] & b'\xf0' to event type
    CONTROLLER_DICTIONARY = {0: "Bank Select",
                             1: "Modulation",
                             2: "Breath Controller",
                             4: "Foot Controller",
                             5: "Portamento Time",
                             6: "Data Entry MSB",
                             7: "Main Volume",
                             8: "Balance",
                             10: "Pan",
                             11: "Expression Controller",
                             12: "Effect Control 1",
                             13: "Effect Control 2",
                             # 0-63 for off, 64-127 for on
                             64: "Damper pedal (sustain)",
                             65: "Portamento",
                             66: "Sostenuto",
                             67: "Soft Pedal",
                             68: "Legato Footswitch",
                             69: "Hold 2",
                             70: "Sound Controller 1 (default: Timber Variation)",
                             71: "Sound Controller 2 (default: Timber/Harmonic Content)",
                             72: "Sound Controller 3 (default: Release Time)",
                             73: "Sound Controller 4, (default: Attack Time)",
                             74: "Sound Controller 5, (default: Brightness)",
                             84: "Portamento Control",
                             91: "Effects 1 Depth (formerly External Effects Depth)",
                             92: "Effects 2 Depth (formerly Tremolo Depth)",
                             93: "Effects 3 Depth (formerly Chorus Depth)",
                             94: "Effects 4 Depth (formerly Detune Depth)",
                             95: "Effects 5 Depth (formerly Phaser Depth)",
                             96: "Data Increment",
                             97: "Data Decrement",
                             98: "Non-Registered Parameter Number (LSB)",
                             99: "Non-Registered Parameter Number (MSB)",
                             100: "Registered Parameter Number (LSB)",
                             101: "Registered Parameter Number (MSB)",
                             121: "Reset All Controllers",
                             122: "Local Control",
                             123: "All Notes Off",
                             124: "Omni Off",
                             125: "Omni On",
                             126: "Mono On (Poly Off)",
                             127: "Poly On (Mono Off)"}
