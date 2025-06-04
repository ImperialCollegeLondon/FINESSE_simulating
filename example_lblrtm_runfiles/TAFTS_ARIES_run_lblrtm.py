"""Run LBLRTM

Turned previous script into modular pieces of code

Authour: Sanjeevani Panditharatne
Written: 30/04/2025
"""

from TAFTS_ARIES_define_inputs import *
from fir_simulation_wrapper import *
from fir_simulation_wrapper import TAFTS_ARIES

# Inputs are specified in define_inputs.py which calls the write_tape5.py script
# These are printed in the output for clarity
print('LBLRTM Exe Location: ',lbl_location+lbl_exe_name)
print('Save Location: ',save_location)

# Call LBLRTM to run simulation
call_lblrtm(lbl_location, lbl_exe_name, save_location, OD)

# # Converts the TAPE12 output from a binary file into a numpy array.
tape12_array = load_tape12(save_location, mode)
high_res_wn = tape12_array[0, :]
high_res_spec = tape12_array[1, :]

# # Apply FINESSE OPD = 1.21 onto a sampling grid of 0.2 cm-1
print("========== Applying TAFTS and ARIES ILS ==========")

TAFTS_apodised_wn, TAFTS_apodised_spectrum = TAFTS_ARIES.TAFTS_apod(high_res_wn, high_res_spec,100,600)
ARIES_apodised_wn, ARIES_apodised_spectrum = TAFTS_ARIES.ARIES_apod(high_res_wn, high_res_spec,600,1600)

print("======== Finishing and Plotting ========")

# Converted to mW
TAFTS_apodised_spectrum_mW = TAFTS_apodised_spectrum.real * 1e6
ARIES_apodised_spectrum_mW = ARIES_apodised_spectrum.real * 1e6

# np.savetxt(save_location+'TAFTS_example_spectrum.txt',np.vstack([TAFTS_apodised_wn,TAFTS_apodised_spectrum_mW]).T,
#            header='Example TAFTS LBLRTM output\nWN (cm^{-1})  Rad(mW m^{-2} sr^{-1} cm)',
#            fmt=['%12.3f','%12.5f'])

# np.savetxt(save_location+'ARIES_example_spectrum.txt',np.vstack([ARIES_apodised_wn,ARIES_apodised_spectrum_mW]).T,
#            header='Example ARIES LBLRTM output\nWN (cm^{-1})  Rad(mW m^{-2} sr^{-1} cm)',
#            fmt=['%12.3f','%12.5f'])


plt.plot(TAFTS_apodised_wn, TAFTS_apodised_spectrum_mW)
plt.plot(ARIES_apodised_wn, ARIES_apodised_spectrum_mW)

plt.xlabel("Wavenumber (cm$^{-1}$)")
plt.ylabel("Radiance (mW m$^{-2}$ sr$^{-1}$ cm)")
plt.savefig(save_location + "Output_Plot.jpg", dpi=300)

print("========== END ==========")
