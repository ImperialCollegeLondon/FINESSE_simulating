[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ImperialCollegeLondon/fir_simulation_wrapper/main.svg)](https://results.pre-commit.ci/latest/github/ImperialCollegeLondon/fir_simulation_wrapper/main)
[![codecov](https://codecov.io/gh/ImperialCollegeLondon/fir_simulation_wrapper/graph/badge.svg?token=DTS433S9E2)](https://codecov.io/gh/ImperialCollegeLondon/fir_simulation_wrapper)
[![CI](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper/actions/workflows/ci.yml)

## Documentation

This contains the code to run LBLRTM and LBLDIS simulations of different far-infrared instruments. This code was compiled by Sanjeevani Panditharatne, and is based on python scripts written by Laura Warwick, Sophie Mosselmans, and Sanjeevani Panditharatne.

This code is currently configured to simulate: FINESSE, FSI (RTTOV), and TAFTS/ARIES 

Contents include:
- **/aux** contains files that describe the ILS of instruments.
- **/docs** contains information about the ILS of each instrument
- **/example_input** contains an example profile and example emissivity profile to be read
- **/example_lblrtm_output** contains example outputs for each of the instruments.
- **/example_lbldis_output** contains example outputs for FSI only.
- **/example_lblrtm_runfiles** contains example runfiles for each instrument that only call LBLRTM.
- **/example_lbldis_output** contains example runfiles for the FSI that calls LBLRTM with the correct settings and then calls LBLDIS. NOTE: LBLDIS is a very slow model. Run at low res to test.
- **/src/fir_simulation_wrapper** folder that includes functions and modules used to interact with LBLRTM outputs


The src/fir_simulation_wrapper folder currently contains the following modules:
- **__init__** used to import functions
- **FINESSE** contains the functions to apply the ILS to simulations and contains the following functions: apply_ILS_sav ; apply_ILS_nc [REQUIRES MODULE REF TO LOAD FUNCTIONS]
- **FSI** contains the functions to apply the ILS to simulations and contains the following functions: rttov_forum_apodise [REQUIRES MODULE REF TO LOAD FUNCTIONS]
- **general_ils_functions** contains functions that could be useful for general spectral treatment: process_spectrum_general
- **module_function_list** contains a list of useful python modules
- **panel_file** contains the scripts used to read TAPE12s
- **PREFIRE** ontains the functions to apply the ILS to simulations and contains the following functions: in_range ; apply_srf ; prefire_simulation
- **run_read_lblrtm** contains the following functions to run and read lblrtm output: call_lblrtm ; load_tape12
- **TAFTS_ARIES** ontains the functions to apply the ILS to simulations and contains the following functions: ARIES_apod ; TAFTS_apod
- **write_lbl_emiss** contains the following functions to write the EMISSIVITY and REFLECTIVITY files required for LBLRTM: write_lbl_emiss
- **write_lbldis_parameter_file** contains the following functions to write the parameter file required for LBLDIS: write_parameter_file
- **write_tape5** contains the following functions to write the TAPE5 file required for LBLRTM: write_tape5_fn

The project setup is documented in [project_setup.md](project_setup.md). Feel free to remove this document (and/or the link to this document) if you don't need it.

## Setup Instructions for Developers

### 1) Download the code

First you need to clone the repository:

```sh
git clone git@github.com:ImperialCollegeLondon/fir_simulation_wrapper.git
```

### 2) (Optionally) make a virtual environment

We recommend that you create a [virtual environment](https://docs.python.org/3/library/venv.html) for `fir_simulation_wrapper` to keep the packages installed separate. You can do this like so:

```sh
python -m venv .venv
```

You then need to activate it for your shell. If you are using `bash` then you can run:

```sh
source .venv/bin/activate
```

(If you are using a different shell, then there are other scripts in the `.venv/bin` folder you can use instead.)

If you're going to use this package often you can add the above piece of code into your ./bashrc file (vi /home/<username>/.bashrc).

### 3) Install the developer dependencies

Next you will want to install the dependencies for `fir_simulation_wrapper` along with the developer tools required to work on the project.

You can do this like so:

```sh
pip install -e .[dev,scripts]
```

<!-- ### Install `pre-commit`

This project contains a configuration file for [`pre-commit`](https://pre-commit.com), a tool which automatically runs specified checks every time you make a commit with Git. The `pre-commit` command-line tool will be installed along with the other developer dependencies, but you **also** have to enable it for this repository, like so:

```sh
pre-commit install
```

Now, whenever you make a Git commit, your changes will be checked for errors and stylistic problems. (For a list of the hooks enabled for this repository, [see the configuration file](./.pre-commit-config.yaml)).

The `pre-commit` hooks will also be run on every pull request by [pre-commit.ci](https://pre-commit.ci). -->

### 4) Set FIR_AUX_PATH

Add this location of your aux path to your .bashrc file so the code can access the auxiliary ILS files.

```sh
vi /home/<<username>>/.bashrc
export FIR_AUX_PATH='/net/thunder/data1/<<username>>/FINESSE_LBLRTM/fir_simulation_wrapper/aux/'
```

### 5) Ready to run

You are now ready to use this Python package to simualte FINESSE spectra using LBLRTM. Note that LBLRTM and the TAPE3 input must be configured separately.
The profile and LBLRTM settings are specified in 'define_inputs.py'. These inputs are read into the example run file. Assuming your virtual environment is activated you can run the test script by doing:

```sh
python example_lblrtm_runfiles/FINESSE_run_lblrtm.py
python example_lbldis_runfiles/FSI_run_lbldis.py

```

## LBLDISv3.0 SPECIFIC INSTRUCTIONS

All of the LBLDIS stuff is based off work done by Rich Bantges and Sanjeevani Panditharatne. The key executables are soft linked to Richard Bantges directories 

The README for LBLDISv3.0 is stored here: /net/sirocco/users/bantges/lbldis.Release_3_0/README.lbldis.Release_3_0.txt

NOTE: Be aware that the resolution = sampling (I think) so you may need higher resolution for things

## TO DO LIST
There are a number of checks that still need to be made to this, particualrly for the LBLDIS wrapper.

## Credits

This package was created with [Copier](https://github.com/copier-org/copier) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
