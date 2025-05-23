"""WRITE_LBL_EMISS

File to write EMISSIVITY and REFLECTIVITY files needed for simulating
upwelling radiation
Author: Sanjeevani Panditharatne
"""
import numpy as np
def write_lbl_emiss(lbl_location,wn,emiss):
    """Function to automatically generate EMISSIVITY and REFLECTIVITY files

    Args:
        lbl_location (str): Path of LBLRTM exe
        wn (np.array): Wavenumber range
        emiss (np.array): Emissivity values
    """
    refl=np.array([1-x for x in emiss])

    with open(lbl_location+'EMISSIVITY', "w+") as file:
        # Record 1.4 
        # V1,V2,DV,NLIM
        file.write("{:10.4f}{:10.4f}{:10.4f}     {:5d}\n".format(wn[0],wn[-1],wn[1]-wn[0],len(wn)))
        for j in range(len(wn)):
            file.write("{:10.7f}{:10.4f}\n".format(emiss[j], wn[j]))

    with open(lbl_location+'REFLECTIVITY', "w+") as file:
        # Record 1.4 
        # V1,V2,DV,NLIM
        file.write("{:10.4f}{:10.4f}{:10.4f}     {:5d}\n".format(wn[0],wn[-1],wn[1]-wn[0],len(wn)))
        for j in range(len(wn)):
            file.write("{:10.7f}{:10.4f}\n".format(refl[j], wn[j]))

    return
