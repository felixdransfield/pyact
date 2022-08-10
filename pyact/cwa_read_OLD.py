# OLD versions of cwa_read functions changed to class based

def read_header_dict(fid, numDBlocks):
    """
    :param fid: Numpy array of bytes
    :param numDBlocks: number of data blocks
    :return: list of unique_serial_code, frequency, start, device,  firmware_version, blocks
    Read file header and return it as a list with following elements
    uniqueSerialCode is unique serial code of used device
    frequency is measurement frequency. All data will be resampled for this frequency.
    start is timestamp in numeric form. To get text representation
    device is "Axivity"
    firmwareVersion is version of firmware
    blocks is number of datablocks with 80 or 120 observations in each
    Unfortunately frequency of measurement is varied in this device.
    """

    # Convert header section (0-42 bytes) from numpy array to bytes
    header = fid[0:42].tobytes()

    # This dictionary defines the different variables contained inside the header (keys)
    # and the location of the bytes that constitute the variable (values)
    header_dict = {
        "header_id": [0, 1],
        "hardware_type": 4,
        "lower_device_id": [5, 6],
        "session_id": [7, 8, 9, 10],
        "upper_device_id": [11, 12],
        "samplerate": 36,
        "version": 41
    }

    # For loop takes the byte location of each variable and assigns the bytes from the header array converted to
    # an integer
    for k, v in header_dict.items():
        if type(v) == int:
            header_dict[k] = header[v]
        else:
            header_dict[k] = int.from_bytes(header[min(v):max(v) + 1], "big")

    # Checking id for the header block is correct
    # TODO convert to string "MD" ?
    if header_dict["header_id"] != 19780:
        # TODO porper error message
        print("Error msg")
        return None
    else:
        if header_dict["hardware_type"] == 64:
            header_dict["hardware_model"] = "AX6"
        else:
            header_dict["hardware_model"] = "AX3"

        if header_dict["upper_device_id"] >= 65535:
            header_dict["upper_device_id"] = 0

        header_dict["serial_code"] = header_dict["upper_device_id"] * 65536 + header_dict["lower_device_id"]
        header_dict["frequency_header"] = round(3200 / (1 << (15 - header_dict["samplerate"] & 15)))
        print(header_dict)

        # Read the first data block without data?
        first_data_block = fid[1024:]
        data = read_data_block_dict(first_data_block, complete=False)
        if data is None:
            # TODO
            print("Error in the first data block reading")
            return None

        return header_dict


def read_data_block_dict(data_block, complete=True):
    """
    #TODO docstring
    :param fid:
    :param complete:
    :return:
    Read one block of data and return list with following elements
    frequency is frequency recorded in this block
    start is start time in nummeric form. To create string representation
        it is necessary to use
            as.POSIXct(start, origin = "1970-01-01", tz=desiredtz)
    temperature is temperature for the block
    battery is battery charge for the block
    light is light sensor measurement for the block
    length is number of observations in the block
    data is matrix with three columns "x", "y", and "z"
    matrix data is presented if complete == TRUE only.

    """

    data_block_dict
    return None


def read_header(fid, numDBlocks):
    """
    :param fid: Numpy array of bytes
    :param numDBlocks: number of data blocks
    :return: list of unique_serial_code, frequency, start, device,  firmware_version, blocks
    Read file header and return it as a list with following elements
    uniqueSerialCode is unique serial code of used device
    frequency is measurement frequency. All data will be resampled for this frequency.
    start is timestamp in numeric form. To get text representation
    device is "Axivity"
    firmwareVersion is version of firmware
    blocks is number of datablocks with 80 or 120 observations in each
    Unfortunately frequency of measurement is varied in this device.
    """
    # Convert header section (0-42 bytes) from numpy array to bytes
    header = fid[0:42].tobytes()

    # Read block header
    id_string = header[0:2]
    # Check for correctness of name
    if id_string.decode() == "MD":
        # TODO comment
        hardware_type = header[4]  # Offset 4
        if hardware_type == 64:
            hardware_type = "AX6"
        else:
            hardware_type = "AX3"
        lower_device_id = int.from_bytes(header[5:7], "big")
        session_id = int.from_bytes(header[7:11], "big")
        upper_device_id = int.from_bytes(header[11:13], "big")
        if upper_device_id >= 65535:
            upper_device_id = 0
        serial_code = upper_device_id * 65536 + lower_device_id
        samplerate_dynrange = header[36]
        frequency_header = round(3200 / (1 << (15 - samplerate_dynrange & 15)))
        if samplerate_dynrange < 0:
            samplerate_dynrange = samplerate_dynrange + 256
        accrange = 16 >> (abs(samplerate_dynrange) >> 6)
        version = header[41]

        # Read the first data block without data
        first_data_block = fid[1024:]
        data = read_data_block(first_data_block, complete=False)
        if data is None:
            # TODO
            print("Error in the first data block reading")
            return None
        # if frequency_header != data.frequency:
        # TODO change to warning? reutrn none? + uncomment
        # print(f"Inconsistent value of measurement frequency: there is"
        # f"{frequency_header} in header and {data.frequency} in the"
        # f"first data block.")
    else:
        return None

    # TODO whatever this is line 134
    # start = as.POSIXct(datas$start, origin = "1970-01-01", tz=desiredtz)

    return_object = {
        "serial_code": serial_code,
        "frequency": frequency_header,
        "start": start,
        "device": "Axivity",
        "firmware_version": version,
        "blocks": numDBlocks,
        "accrange": accrange,
        "hardware_type": hardware_type
    }

    return return_object


def unsigned16(x):
    """Auxiliary function for normalisation of unsigned integers"""
    if x < 0:
        x = x + 256  # 2^8
    return x


def unsigned16(x):
    """Auxiliary function for normalisation of unsigned integers"""
    if x < 0:
        x = x + 65536  # 2^16
    return x


def read_data_block(data_block, complete=True):
    """
    #TODO docstring
    :param fid:
    :param complete:
    :return:
    Read one block of data and return list with following elements
    frequency is frequency recorded in this block
    start is start time in nummeric form. To create string representation
        it is necessary to use
            as.POSIXct(start, origin = "1970-01-01", tz=desiredtz)
    temperature is temperature for the block
    battery is battery charge for the block
    light is light sensor measurement for the block
    length is number of observations in the block
    data is matrix with three columns "x", "y", and "z"
    matrix data is presented if complete == TRUE only.

    """
    # TODO comments (all offsets)
    data_block = data_block.tobytes()

    # Check the block header
    id_string = data_block[0:2]
    if len(id_string) == 0 or id_string.decode() != "AX":
        return None
    else:
        # ts_offset = int.from_bytes(data_block[4:6], "big")
        # timestamp = int.from_bytes(data_block[14:22], "big")
        # offset18 = unsigned16(int.from_bytes(data_block[18:20], "big"))

        # light = 2 ^ (3.0 * (offset18 / 512.0 + 1.0)) # used for AX3, but this seems to have been incorrect
        # light = offset18 & 1023 # converted from hex value CHECK!
        # accel_scale_code = offset18 >> 13
        # accel_scale = 1 / (2 ^ (8 + accel_scale_code))
        # gyro_range_code = math.floor(offset18 / 1024) % 8
        # gyro_range = 8000 / (2 ^ gyro_range_code)

        # Read and recalculate temperature u16 in offset 20
        # temperature = (150.0 * int.from_bytes(data_block[20:22]) - 20500.0) / 1000.0
        # Read and recalculate battery charge u8 in offset 23

        # TODO FINISH read data block function

        return "hello"
