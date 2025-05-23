"""Functions to write parameter file for lbldis
Author: Sanjeevani Panditharatne
"""

import numpy as np
import os

def write_parameter_file(database,alt,eff_rad,ref_wv,tau_1,  
                         sfc_em, 
                         path_wdir, 
                         lbldisdir,
                         t_surf=-1,
                         angle=180,
                         ssp=[os.environ['FIR_AUX_PATH']+'/ssp_db.mie_wat.gamma_sigma_0p100',
                              os.environ['FIR_AUX_PATH']+'baum_ghm_ssp_heb'], 
                         start_wn = 150,
                         end_wn=1600,
                         inc_wn=1/100, 
                         sza=0, 
                         scatter = True, 
                         kurucz=os.environ['FIR_AUX_PATH']+'solar.kurucz.rad.1cm-1binned.full_disk.asc', 
                         log_re=False):
    '''
    Write parameter file for LBLDIS
    
    Parameter
    ---------
    database,alt,eff_rad,ref_wv,tau_1: array
        Values to be input, all need to be the same length

    path_wdir : str
        Path to output of TCWret

    lbldisdir : str
        Path to lblrtm output

    t_surf : float
        Surface temperature. If negative, surface temperature equals temperature of 
        lowermost atmospheric level

    angle  : string  
        Angular view. Default is upwelling.
        
    ssp : list
        Names of single-scattering databases
        
    start_wn, end_wn, inc_wn : float
        Wavenumber range NOTE inc_wn is the increment that you want / 100 - not sure why
        
    sza : float
        Solar Zenith Angle
        
    cloud_grid : list
        Layers of cloud
        
    scatter : bool
        Use scatter in LBLDIS
        
    kurucz : str
        Name of Kurucz database
        
    sfc_em : list
        Surface emissivity
        
    log_re : bool
        Use logarithmic r_eff
        
        
    '''
    
    if scatter:
        sign = 1
    else:
        sign = -1
            
    with open("{}/lbldis.param".format(path_wdir), "w") as file_:
        file_.write("LBLDIS parameter file\n")
        file_.write("16		# Number of streams\n")
        file_.write("{:04.1f} 30. 1.0	#Solar ".format(sza))
        file_.write(" zenith angle (deg), relative azimuth (deg), solar distance (a.u.)\n")
        file_.write("{}           # Zenith angle (degrees): 0 ->  upwelling, 180 -> downwelling\n".format(angle))
        file_.write("{:4.1f} {} {}".format(start_wn,end_wn,inc_wn/100))
        file_.write("# v_start, v_end, and v_delta [cm-1]\n")
        file_.write("{}               ".format(sign))
        file_.write("# Cloud parameter option flag: ")
        file_.write("# 0: reff and numdens, >=1:  reff and tau - database height effective_radius ref_wavelength in cm-1 tau_1 tau_2...\n")
        file_.write("{}".format(np.shape(alt)[0]))
        file_.write("               # Number of cloud layers\n")

        for x in range(np.shape(alt)[0]):
            if log_re:
                print('not compatible')
                break
            else:
                file_.write("{:5.3f} {:5.3f} {:5.3f} {:8.3f}{:10.3E}".format(database[x],alt[x],eff_rad[x],ref_wv[x], tau_1[x]))
            file_.write("\n")

        file_.write("{}\n".format(lbldisdir))
        file_.write("{}\n".format(kurucz))
        num_db = len(ssp)
        file_.write("{}       # Number of scattering property databases\n".format(num_db))
        for database in ssp:
            file_.write(database + "\n")
        file_.write("{}	     # Surface temperature (specifying a negative".format(t_surf))
        file_.write("value takes the value from profile)\n")
        file_.write("{}	     #Number of surface spectral emissivity lines (wnum, emis)\n".format(len(sfc_em[1])))
        for y in range(len(sfc_em[1])):
            file_.write("{:10.3f}     {:5.3f}\n".format(sfc_em[0,y], sfc_em[1,y]))
    return
