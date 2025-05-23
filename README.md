[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ImperialCollegeLondon/fir_simulation_wrapper/main.svg)](https://results.pre-commit.ci/latest/github/ImperialCollegeLondon/fir_simulation_wrapper/main)
[![codecov](https://codecov.io/gh/ImperialCollegeLondon/fir_simulation_wrapper/graph/badge.svg?token=DTS433S9E2)](https://codecov.io/gh/ImperialCollegeLondon/fir_simulation_wrapper)
[![CI](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper/actions/workflows/ci.yml)

## Badges

(Customize these badges with your own links, and check <https://shields.io/> or <https://badgen.net/> to see which other badges are available.)

| fair-software.eu recommendations | |
| :-- | :--  |
| (1/5) code repository              | [![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper) |
| (2/5) license                      | [![github license badge](https://img.shields.io/github/license/ImperialCollegeLondon/fir_simulation_wrapper)](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper) |
| (3/5) community registry           | [![RSD](https://img.shields.io/badge/rsd-fir_simulation_wrapper-00a3e3.svg)](https://www.research-software.nl/software/fir_simulation_wrapper) [![workflow pypi badge](https://img.shields.io/pypi/v/fir_simulation_wrapper.svg?colorB=blue)](https://pypi.python.org/project/fir_simulation_wrapper/) |
| (4/5) citation                     | |
| (5/5) checklist                    | [![workflow cii badge](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>/badge)](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>) |
| howfairis                          | [![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu) |
| **Other best practices**           | &nbsp; |
| **GitHub Actions**                 | &nbsp; |
| Build                              | [![build](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper/actions/workflows/build.yml/badge.svg)](https://github.com/ImperialCollegeLondon/fir_simulation_wrapper/actions/workflows/build.yml) |

## Documentation

This contains the code to run LBLRTM simulations of FINESSE spectra which is separate from the processing code to read and calibrated FINESSE interferograms.

Code is based on work done by Laura Warwick, Sophie Mosselmans, and Sanjeevani Panditharatne.

Contents include:

- **/example_input** contains an example profile to be read
- **/example_output** contains an example output and plot
- **/src** folder that includes functions and modules used to interact with LBLRTM outputs which should not need to be edited
- **define_inputs.py** which is used to input profile variables, input and output paths, and specify lblrtm version
- **run_lblrtm_FINESSE.py** the script to write the TAPE5, run the exe, and apply the FINESSE instrument line shape
- **EM27_ILS_test1_3_25.sav** is the EM27 ILS used for version 001 of the 2025_WHAFFFERS deliverarables (May 2025)

Required modules are in src/module_function_list.py

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

Set this to the location of your aux path so the code can access the auxiliary ILS files.

```sh
export FIR_AUX_PATH='/net/thunder/data1/sp1016/FINESSE_LBLRTM/fir_simulation_wrapper/aux/'
```

### 5) Ready to run

You are now ready to use this Python package to simualte FINESSE spectra using LBLRTM. Note that LBLRTM and the TAPE3 input must be configured separately.
The profile and LBLRTM settings are specified in 'define_inputs.py'. These inputs are read into the example run file. Assuming your virtual environment is activated you can run the test script by doing:

```sh
python example_runfiles/run_lblrtm_FINESSE.py
```

## Credits

This package was created with [Copier](https://github.com/copier-org/copier) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
