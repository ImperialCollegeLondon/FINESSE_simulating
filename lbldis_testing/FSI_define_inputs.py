import numpy as np
from fir_simulation_wrapper import write_tape5 as wr
from fir_simulation_wrapper import write_lbl_emiss as wr_e
from fir_simulation_wrapper import write_lbldis_parameter_file as wr_p
import os

# Specify location to save the output files
save_location ="/net/thunder/data1/sp1016/FINESSE_LBLRTM/fir_simulation_wrapper/example_lbldis_output/FSI/"

# Specify location of profiles
profile_folder = "/net/thunder/data1/sp1016/FINESSE_LBLRTM/fir_simulation_wrapper/example_input/"

# ===================== INPUTS FOR LBLRTM ===================================
# Specify location of LBLRTM executable
lbl_location = "/net/thunder/data1/sp1016/lblrtm_12.17/"
lbl_exe_name = "lblrtm_v12.17_linux_intel_sgl"

# Specify atmospheric profile (note example profile has fummy z variable)
# See write_tape_5.py instructions for types of atmosphere and setting units
atmospheric_profile_name = profile_folder + "example_profile.txt"
pressure, z, temp, h2o, o3 = np.loadtxt(atmospheric_profile_name, unpack=True)

# Also set yaxis flag to note running in Pressure ('P') or Altitude ('A')
yaxis_flag = "P"

atm = 5  # Sets other gases to standard profiles

# Set flag if units not ppmv - must be included as input for write_tape5 function
h2o_flag = "H"
o3_flag = "C"

# Specify emissivity if desired
emissivity_profile_name = profile_folder + "emissivity_example.txt"
wn,emiss=np.loadtxt(emissivity_profile_name,unpack=True)
wr_e.write_lbl_emiss(lbl_location,wn,emiss)

# Specify view: angle = 0 for downwelling and =180 for upwelling
angle = 180
h_start = pressure[0]  # Radiation calculation starts from altitude in hPa
h_obs = pressure[-1]  ## Pressure height of observation (in this case the ground)

h_start_blackbody_surface = False  # Assuming black body at
h_start_temp = temp[0]

# Set the wavenumber range and resolution
# Note Wavenumber>101 for database
wn_range = [150, 1600]
res = 0.1

# Set the mode
mode = 1  # 1 = radiance, 0 = transmission

# ============= LBLRTM REQUIREMENTS FOR LBLDIS ===============
OD = 0  # 0 = no ODint files (ODdeflt files still made for LBLDIS)

wr.write_tape5_lbldis_fn(
    z ,
    pressure,
    temp,
    h2o,
    h_start_temp,
    h_obs,
    h_start,
    wn_range,
    angle,
    atm,
    mode,
    od=OD,
    t5=lbl_location + "/TAPE5",
    h2o_flag=h2o_flag,
    o3_flag=o3_flag,
    yaxis_flag=yaxis_flag,
    blackbody=h_start_blackbody_surface,
    res=res,
)

# ===================== INPUTS FOR LBLDIS ===================================

# Specify location of LBLDIS executable
lbldis_location = '/net/thunder/data1/sp1016/lbldis/'

# Specify output filename
output_filename = save_location+'lbldis_simulation'

# Which single scattering property database?
# Top one is water ssp
# Bottom one is the ice ssp for a given habit
ssp=[os.environ['FIR_AUX_PATH']+'ssp_db.mie_wat.gamma_sigma_0p100',
    os.environ['FIR_AUX_PATH']+'baum_ghm_ssp_heb']

# Load cloud profile. 
# Cloud parameter option flag: # 0: reff and numdens, 
# >=1:  reff and tau - database height effective_radius ref_wavelength in cm-1 tau_1 tau_2...
#       database specifies which of ssp is used
# Example profile contains reff and tau
cloud_profile_name = profile_folder+'example_cloud_profile.txt'
database,alt,eff_rad,ref_wv,tau_w = np.loadtxt(cloud_profile_name,unpack=True)


# Convert already defined LBLRTM inputs into LBLDIS inputs
if h_start_blackbody_surface==False:
    sfc_em = np.vstack([wn,emiss]).T
else:
    # Define bb SE
    wn = np.arange(wn_range[0]+10,wn_range[1]-10,1)
    sfc_em = np.vstack([wn,np.full_like(wn,1)]).T

# Set surface temperature to value at bottom of profile
#  (i/e in this case it's never TOA temperature)
if angle==180:
    t_surf=h_start_temp
else:
    t_surf=temp[0]

wr_p.write_parameter_file(database,alt,eff_rad,ref_wv,tau_w,  
                        sfc_em, 
                        save_location, 
                        lbldis_location,
                        t_surf=t_surf,
                        angle=angle,
                        ssp=ssp, 
                        start_wn = wn_range[0],
                        end_wn=1200,
                        inc_wn=1, 
                        log_re=False)

