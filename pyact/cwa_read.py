import numpy as np
from pyact.CWA import CWAHeader, CWABlock


def cwa_read(filename, start=0, end=0, progressBar=False, desiredtz="", configtz=[], interpolationType=1):
    # TODO comment properly
    if len(configtz) == 0:
        #configtz = desiredtz
        configtz = None

    def read_header(fid):
        header = CWAHeader(fid[0:42].tobytes())

        if header.header_id != 19780:
            print("Error")
        else:
            # skip 982 bytes and got to first data block
            # To get start date
            data = CWABlock(fid[1024:].tobytes(), configtz, complete=False)
            if data is None:
                # TODO
                print("Error in the first data block reading")
                return None
            elif header.frequency != data.frequency:
                # TODO change to warning? reutrn none? + uncomment
                print(f"Inconsistent value of measurement frequency: there is"
                      f"{header.frequency} in header and {data.frequency} in the"
                      f"first data block.")
            else:
                header.start = data.start

                #printing out complete header attributes
                attrs = vars(header)
                print(', '.join("%s: %s" % item for item in attrs.items()))\

        return header


    # Main Function - reads binary file as numpy array
    try:
        dtype = np.dtype("B")
        with open(filename, "rb") as f:
            fid = np.fromfile(f, dtype)
    except IOError:
        print('Error While Opening the file!')

    # read_header_dict(fid, 3)
    header = read_header(fid)


    return None
