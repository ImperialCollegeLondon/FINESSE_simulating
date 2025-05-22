# import python packages
import math as math
import shutil
import os
import numpy as np
import subprocess as sub
import glob as glob
from scipy.fftpack import fft, ifft
from scipy.interpolate import interp1d
from scipy.io import readsav
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt 
import struct
from codecs import decode