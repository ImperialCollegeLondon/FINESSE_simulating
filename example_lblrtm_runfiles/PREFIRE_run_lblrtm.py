"""Run LBLRTM

Turned previous script into modular pieces of code

Authour: Sanjeevani Panditharatne
Written: 30/04/2025
"""

from PREFIRE_define_inputs import *
from fir_simulation_wrapper import *
from fir_simulation_wrapper import PREFIRE

# Inputs are specified in define_inputs.py which calls the write_tape5.py script
# These are printed in the output for clarity
print('LBLRTM Exe Location: ',lbl_location+lbl_exe_name)
print('Save Location: ',save_location)

# # Call LBLRTM to run simulation
call_lblrtm(lbl_location, lbl_exe_name, save_location, OD)

# # Converts the TAPE12 output from a binary file into a numpy array.
tape12_array = load_tape12(save_location, mode)
high_res_wn = tape12_array[0, :]
high_res_spec = tape12_array[1, :]

# # Apply PREFIRE ILS
print("========== Applying PREFIRE ILS ==========")
apodised_spectrum_ds = PREFIRE.prefire_simulation(high_res_spec, high_res_wn, 'TIRS1', spec_range=(wn_range[0],wn_range[1]), sc=0, reject_mask=0b000011, verbose=False)

print("======== Finishing and Plotting ========")

# Converted to mW
# apodised_spectrum_mW = apodised_spectrum * 1e6

plt.plot(apodised_spectrum_ds['channel'], apodised_spectrum_ds['channel_radiance'],marker='.')
# np.savetxt(save_location+'PREFIRE_example_spectrum.txt',np.vstack([apodised_spectrum_ds['channel'], apodised_spectrum_ds['channel_radiance']]).T,
#            header='Example PREFIRE LBLRTM output\nWL (microns)  Rad(mW m^{-2} sr^{-1} cm)',
#            fmt=['%12.3f','%12.5f'])

plt.xlabel("Wavelength ($\mu m$)")
plt.ylabel("Radiance (mW m$^{-2}$ sr$^{-1}$ cm)")
plt.savefig(save_location + "Output_Plot.jpg", dpi=300)

print("========== END ==========")
