"""Run LBLRTM

Turned previous script into modular pieces of code

Authour: Sanjeevani Panditharatne
Written: 30/04/2025
"""

from FSI_define_inputs import *
from fir_simulation_wrapper import *
from fir_simulation_wrapper import FSI

# Inputs are specified in define_inputs.py which calls the write_tape5.py script
# These are printed in the output for clarity
print('LBLRTM Exe Location: ',lbl_location+lbl_exe_name)
print('Save Location: ',save_location)

# Call LBLRTM to run simulation - note the output TAPES cannot be read by load_tape12 
# using the LBLDIS required settings at the moment
# call_lblrtm(lbl_location, lbl_exe_name, save_location, OD)

# Run LBLDIS to run simulation
call_lbldis(lbldis_location, save_location,output_filename)


# ============= READ AND PLOT LBLRTM SIMULATION
# # Converts the TAPE12 output from a binary file into a numpy array.
# tape12_array = load_tape12(save_location, mode)
# high_res_wn = tape12_array[0, :]
# high_res_spec = tape12_array[1, :]

# print("========== Applying FORUM ILS ==========")
# apodised_wn, apodised_spectrum = FSI.rttov_forum_apodise(high_res_wn, high_res_spec)

# print("======== Finishing and Plotting ========")

# # Converted to mW
# apodised_spectrum_mW = apodised_spectrum * 1e6

# plt.plot(apodised_wn, apodised_spectrum_mW)

# ============== READ AND PLOT LBLDIS SIMULATION
lbldis_simulation = xr.open_dataset(output_filename+'.cdf')
lbldis_simulation=lbldis_simulation.sel(n_instances=0)
high_res_wn = lbldis_simulation.wnum.values
high_res_spec = lbldis_simulation.radiance.values

clear_wn, clear_spectrum_mW = np.loadtxt('/data1/sp1016/FINESSE_LBLRTM/fir_simulation_wrapper/example_output/FSI/FSI_example_spectrum.txt', unpack = True)
plt.plot(clear_wn, clear_spectrum_mW*1E1,label='Clear')

print("========== Applying FORUM ILS ==========")
# apodised_wn, apodised_spectrum_mW = FSI.rttov_forum_apodise(high_res_wn, high_res_spec)
plt.plot(high_res_wn, high_res_spec, label='Cloudy')

# plt.plot(apodised_wn, apodised_spectrum_mW, label='Cloudy')

plt.xlabel("Wavenumber (cm$^{-1}$)")
plt.ylabel("Radiance (mW m$^{-2}$ sr$^{-1}$ cm)")

# ========== PLOTTING THE LBLRTM EXAMPLE SPECTRUM FOR REFERENCE =======
plt.legend()
plt.savefig(save_location + "Output_Plot.jpg", dpi=300)

print("========== END ==========")
