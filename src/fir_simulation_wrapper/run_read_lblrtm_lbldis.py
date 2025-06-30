"""RUN_READ_LBLRTM_LBLDIS

Functions to run the LBLRTM executable and read TAPE12 output
Function to run the LBLDIS executable

"""

from fir_simulation_wrapper.module_function_list import *
from fir_simulation_wrapper.panel_file import *

# This class allows you to change the current working
# directory as you would in linux. IT is needed to run
# LBLRTM later on. You coud probably
# do this yourself using os if you prefered
class cd:
    """Context manager for changing the current working directory
    from https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python/13197763#13197763
    """

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def call_lblrtm(lbl_location, lbl_exe_name, save_location, OD):
    """Runs the LBLRTM executable

    Args:
        lbl_location (_path_): location of local LBLRTM exeutable
        sav_location (_path_): save location
        OD (_variable_): specifies if writing out seperate optical depth files
                           (0 = no, 1 = yes)
    """
    print("========== Calling LBLRTM ==========")
    # Change folder to where the LBLRTM executable is located
    with cd(lbl_location):
        # Run LBLRTM (the string should be the name of the LBLRTM executable)
        sub.call(lbl_exe_name)

    # Move all files somewhere to be saved
    # IF this step is skipped, LBLRTM will overwrite these
    # files when it is run again
    shutil.move(lbl_location + "TAPE5", save_location + "/TAPE5")
    shutil.move(lbl_location + "TAPE6", save_location + "/TAPE6")
    shutil.move(lbl_location + "TAPE11", save_location + "/TAPE11")
    shutil.move(lbl_location + "TAPE12", save_location + "/TAPE12")

    if os.path.isfile(lbl_location+'TAPE7')==True:
        shutil.move(lbl_location+"TAPE7", save_location + "/TAPE7")

    # Move emissivity and reflectivity files if created
    if os.path.isfile(lbl_location+'EMISSIVITY')==True:
        shutil.move(lbl_location + "EMISSIVITY", save_location + "/EMISSIVITY")
        shutil.move(lbl_location + "REFLECTIVITY", save_location + "/REFLECTIVITY")

    # Also move OD files if created
    all_files = os.listdir(lbl_location)
    for file in all_files:
        if 'OD' in file:
            shutil.move(lbl_location + file, save_location + file)
    return


def load_tape12(save_location, mode):
    """Load the TAPE12 (that is in binary format) into a numpy array

    Args:
        save_location (path): path of TAPE12 specified in main script
        mode (int): see write_tape5.py: 0 - radiances only 1- radiances and transmittances
    Returns:
        tape12_array (array): first column is the wavenumber and second is radiances (optionally) transmittance is third

    Author: Sanjeevani Panditharatne (based on LW + SM script)
    """
    print("==== Loading TAPE12 as Numpy Array ====")
    panel_data = panel_file(save_location + "TAPE12", do_load_data=True)
    if mode == 1:
        rad_in_raw = panel_data.data1
        wn_in_raw = panel_data.v
        tape12_array = np.vstack([wn_in_raw, rad_in_raw])
    elif mode == 0:
        trans_in_raw = panel_data.data1
        rad_in_raw = panel_data.data1
        wn_in_raw = panel_data.v
        tape12_array = np.vstack([wn_in_raw, rad_in_raw, trans_in_raw])
    return tape12_array


def call_lbldis(lbldis_location, save_location,output_filename):
    """Runs the LBLDIS executable

    Creates and runs a bash script to run the LBLDIS exe.

    Args:
        lbldis_location (_path_): location of local LBLDIS exeutable
        save_location (_path_): save location
        output_filename (_path_): written in defined_inputs

    """

    # lists all the files and copies them into LBLDIS folder
    for file in os.listdir(save_location):
        if 'TAPE' in file or 'ODdeflt_' in file or 'param' in file:
            os.system('cp '+ save_location+file +' '+ lbldis_location+file)
            os.system('cp '+ save_location+file +' '+ lbldis_location+file)
    print('LBLDIS Location: ' +lbldis_location)
    print("===== Starting LBLDIS =====")
    print('Remember this will continue to append an existing file!')
    # Change folder to where the LBLRTM executable is located
    with cd(lbldis_location):
        # Run LBLDIS (the string should be the name of the LBLRTM executable)
        with open("run_disort.sh".format(save_location), "w") as file_:
            file_.write("#!/bin/bash\n")

            file_.write('lbldis_sgl_exe '+ save_location+'lbldis.param'+' 0 '+output_filename) #lbldis_sgl_exe parameter_test 0 test_output'
        sub.call(["bash", "run_disort.sh".format(save_location)])

    for file in os.listdir(lbldis_location):
        if 'TAPE' in file and os.path.isdir(file)==False:
            os.system('rm '+ lbldis_location+file)
        if 'ODdeflt_' in file:
            os.system('rm '+ lbldis_location+file)

    os.system('cp '+ 'lbldis.param' +' '+ save_location+'lbldis.param')