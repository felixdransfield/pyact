import os
from pyact.cwa_read import cwa_read

def process_raw(datadir, outputdir, f0, f1):
    # List All accelerometer files
    # TODO: check if correct files eg .cwa
    fnames = os.listdir(datadir)
    fnames = fnames[f0:f1]
    for file in fnames:
        file = datadir + "/" + file
        cwa_read(file)


    # TODO: check if already processed?



    # Inspecting file

    return None


