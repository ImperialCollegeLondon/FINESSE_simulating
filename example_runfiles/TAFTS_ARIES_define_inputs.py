import numpy as np
from fir_simulation_wrapper import write_tape5 as wr
from fir_simulation_wrapper import write_lbl_emiss as wr_e

# Specify location of LBLRTM executable
lbl_location = "/net/thunder/data1/sp1016/lblrtm_12.17/"
lbl_exe_name = "lblrtm_v12.17_linux_intel_dbl"

# Specify location to save the output files
save_location ="/net/thunder/data1/sp1016/FINESSE_LBLRTM/fir_simulation_wrapper/example_output/TAFTS_ARIES/"

# Specify location of profiles
profile_folder = "/net/thunder/data1/sp1016/FINESSE_LBLRTM/fir_simulation_wrapper/example_input/"

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
wn_range = [100, 1600]
res = 0.01

# Set the mode
mode = 1  # 1 = radiance, 0 = transmission
OD = 0  # 0 = no optical depth files

wr.write_tape5_fn(
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
