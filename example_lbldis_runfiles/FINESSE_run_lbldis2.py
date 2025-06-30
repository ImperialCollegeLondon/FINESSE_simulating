"""Run LBLRTM

Turned previous script into modular pieces of code

Authour: Sanjeevani Panditharatne
Written: 30/04/2025
"""

from FINESSE_define_inputs2 import *
from fir_simulation_wrapper import *
from fir_simulation_wrapper import FINESSE

# Inputs are specified in define_inputs.py which calls the write_tape5.py script
# These are printed in the output for clarity
print('LBLRTM Exe Location: ',lbl_location+lbl_exe_name)
print('Save Location: ',save_location)

# Call LBLRTM to run simulation - note the output TAPES cannot be read by load_tape12 
# using the LBLDIS required settings at the moment
# call_lblrtm(lbl_location, lbl_exe_name, save_location, OD)

# Run LBLDIS to run simulation
# call_lbldis(lbldis_location, save_location,output_filename)

# ============= READ AND PLOT EXAMPLE LBLRTM SIMULATION
# Loading preconverted clear sky spectrum
clear_wn, clear_spectrum_mW = np.loadtxt('/data1/sp1016/FINESSE_LBLRTM/fir_simulation_wrapper/example_output/FINESSE/FINESSE_example_spectrum.txt', unpack = True)

# # Apply FINESSE OPD = 1.21 onto a sampling grid of 0.2 cm-1
print("========== Applying FINESSE ILS TO LBLDIS SIMULATION ==========")
lbldis_simulation = xr.open_dataset(output_filename+'.cdf')
lbldis_simulation=lbldis_simulation.sel(n_instances=0)
high_res_wn = lbldis_simulation.wnum.values
high_res_spec = lbldis_simulation.radiance.values

wn_out, rad_out = process_spectrum_general(
    high_res_wn, high_res_spec, 0.2, 350, 1400, 1.21
)

# # Apply the FINESSE instruMent line shape
# Andoya ILS: EM27_ILS.sav
# WHAFFFERS ILS: EM27_ILS_test1_3_25.sav
ILS_LOCATION = os.environ['FIR_AUX_PATH']+"EM27_ILS_test1_3_25.sav" 
ils = FINESSE.readsav(ILS_LOCATION)
ILS = ils["em27_ils"][:]
apodised_wn, apodised_spectrum = FINESSE.apply_ILS_sav(ILS, wn_out, rad_out, pad_length=10)

print("======== Finishing and Plotting ========")
plt.plot(clear_wn, clear_spectrum_mW*1E1,label='Clear')
plt.plot(apodised_wn, apodised_spectrum,label='Cloudy')

plt.xlabel("Wavenumber (cm$^{-1}$)")
plt.ylabel("Radiance (mW m$^{-2}$ sr$^{-1}$ cm)")

plt.legend()
plt.savefig(save_location + "Output_Plot.jpg", dpi=300)

print("========== END ==========")
