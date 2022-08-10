import os
import fnmatch

from pyact.process_raw import process_raw


def pyact(datadir, outputdir, f0 = 0, f1 = 0):
    # TODO: Get input variables (line 6)

    # Check datadir and outputdir exist and are directories
    if not os.path.exists(datadir):
        print("Directory specified by argument datadir, does not exist")
        exit()


    if not os.path.exists(outputdir):
        print("Directory specified by argument outputdir, does not exist")
        exit()

    # Establish default start / end file index
    # if f0 == f1 default arguments were used - therefore default is to use every file in datadir
    if f1 == f0:
        # TODO: add different types of file extension
        f1 = len(fnmatch.filter(os.listdir(datadir), '*.cwa'))

    # TODO: Establish which parts (1-5)
    # TODO: Config file used?
    # TODO: Extract parameters from user input of config file
    # TODO: Print Header to console


    # Part 1 Processing raw
    dopart1 = True
    if dopart1:
        process_raw(datadir, outputdir, f0, f1)



    return None

if __name__ == "__main__":
    datadir = "/Users/felixdransfield/Desktop/Test_actigraphy/data/raw"
    outputdir = "/Users/felixdransfield/Desktop/Test_actigraphy/output"


    pyact(datadir, outputdir, 0, 4)