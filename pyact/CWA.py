import datetime
import math


def bytes_to_int(bytes):
    return int.from_bytes(bytes, "big")


def timestamp_decoder(coded, fraction, shift, configtz):

    # Extract parts of the date using Bitwise operations

    # OLD HEXIDECIMAL
    # year = (coded >> 26) & 0x3fL)) + 2000
    # month = (coded >> 22) & 0x0fL
    # day = (coded >> 17) & 0x01f
    # hours = (coded >> 12) & 0x01fL
    # mins = (coded >> 6) & 0x3fL
    # secs = coded  & 0x3fL

    year = ((coded >> 26) & 63) + 2000
    month = (coded >> 22) & 15
    day = (coded >> 17) & 31
    hours = (coded >> 12) & 31
    mins = (coded >> 6) & 63
    secs = coded & 63

    # convert parts of date to datetime object
    # decoded_timestamp = datetime.datetime(year, month, day, hour=hours, minute=mins, second=secs, tzinfo=configtz)

    return [year, month, day, hours, mins, secs]


def unsigned16(x):
    """Auxiliary function for normalisation of unsigned integers"""
    if x < 0:
        x = x + 65536 #2^16
    return x


class CWAHeader:
    def __init__(self, bytes):
        self.device = "Axivity"
        self.header_id = bytes_to_int(bytes[0:2])
        if bytes[4] == 64:
            hardware_type = "AX6"
        else:
            hardware_type = "AX3"
        self.hardware_type = hardware_type
        lower_device_id = bytes_to_int(bytes[5:6])
        upper_device_id = bytes_to_int(bytes[11:12])
        if upper_device_id >= 65535:
            upper_device_id = 0
        self.serial_code = upper_device_id * 65536 + lower_device_id
        sample_rate = bytes[36]
        self.frequency = round(3200 / (1 << (15 - sample_rate & 15)))
        self.firmware_version = bytes[41]


class CWABlock:
    def __init__(self, bytes, configtz, complete = True):
        self.header_id = bytes_to_int(bytes[0:2])
        ts_offset = bytes_to_int(bytes[4:6])
        self.timestamp = bytes_to_int(bytes[14:18])
        # Get light u16 in offset 18
        offset18 = unsigned16(bytes_to_int(bytes[18:20]))
        self.light = offset18 & 1023 # converted from hex value CHECK!
        # accel_scale_code = offset18 >> 13
        # accel_scale = 1 / (2 ^ (8 + accel_scale_code))
        # gyro_range_code = math.floor(offset18 / 1024) % 8
        # gyro_range = 8000 / (2 ^ gyro_range_code)

        # Read and recalculate temperature u16 in offset 20
        temp = bytes_to_int(bytes[20:22])
        self.temperature = (150 * temp -20500.0) / 1000.0

        # Read and recalculate battery charge u8 in offset 23
        batt = bytes[23]
        self.battery_charge = (3.0 * batt) / 512.0 + 1.0

        #TODO find out what this is

        # sampling rate in one of file format u8 in offset 24
        samplerate_dynrange = bytes[24]
        temp = bytes_to_int(bytes[26:28])
        self.block_length = bytes_to_int(bytes[28:30])

        # auxiliary variables
        shift = 0
        fractional = 0
        # Consider two possible formats.
        # Very old file have zero in offset 24 and frequency in offset 26
        if samplerate_dynrange != 0:
            # value in offset 26 is index of measurement with whole number of seconds
            shift = temp
            # If tsOffset is not null then timestamp offset was artificially
            # modified for backwards-compatibility ... therefore undo this..
            # TODO hexidicmal conversion check!!!
            if ts_offset & 32768 != 0:
                self.frequency = round(3200 / (1 << (15 - samplerate_dynrange & 15)))
                accrange = 16 >> abs(samplerate_dynrange >> 6)
                # Need to undo backwards-compatible shim:
                # Take into account how many whole samples the fractional part
                # of timestamp accounts for:
                #   relativeOffset = fifoLength
                #        - (short)(((unsigned long)timeFractional * AccelFrequency()) >> 16);
                #   nearest whole sample
                #       whole-sec   | /fifo-pos@time
                #          |        |/
                #    [0][1][2][3][4][5][6][7][8][9]
                # use 15-bits as 16-bit fractional time
                # TODO hexidicmal conversion check!!!
                fractional = (ts_offset & 32767) << 1
                # frequency is truncated to int in firmware
                shift = shift + (fractional * self.frequency) >> 16
            #TODO hexidecimal conversion check!!
            elif ts_offset & 32768 == 0:
                self.frequency = round(3200 / (1 << (15 - samplerate_dynrange & 15)))
            else:
                # Very old format, where offset 26 contains frequency
                self.frequency = temp

        #TODO sort this
        self.start = timestamp_decoder(self.timestamp, fractional, (-shift / self.frequency), configtz)
        #self.start = timestamp_decoder(timestamp, fractional, -shift / self.frequency)
        # TODO read data if neccesary
        # if complete == True

