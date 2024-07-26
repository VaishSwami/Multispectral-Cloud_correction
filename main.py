# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 12:55:05 2024

@author: Vaishali Swaminathan
"""

import numpy as np
import skimage.color
import skimage.io
import skimage.viewer
#from matplotlib import pyplot as plt
import micasense.image as image
import micasense.panel as panel
import micasense.metadata as metadata
import micasense.utils as msutils
import micasense.capture as capture
import micasense.dls as dls
import datetime, pytz, os, glob,timeit
from math import pi
import subprocess
from PIL import Image
from joblib import Parallel, delayed
import sys
print(os.getcwd())
sys.path.append(os.getcwd())

from CRP import compute_irrad_correction
from Shadow_correction import DLS_correction,DLS_proximity_calibration
from Metadata_handler import metadata_extract, target_liner_regression,irradiance_proximity_matching, combine_irrad_proximity_list
exiftoolPath=os.path.normpath(os.environ.get('exiftoolpath'))
start_time= timeit.default_timer()

### Step 1: CRP-based calibration - optional 
## If you want to use the CRP panel for calibrating the individual images, select CRP = 1, else CRP = 0
CRP = 0
if CRP == 0: ##Recommended
    panel_corr= [1.0,1.0,1.0,1.0,1.0]  
elif CRP == 1:
    panle_folder_path=r'...\Example Dataset\CRP'
    panel_img_name='IMG_0006'
    bounding_box=20
    panel_corr= compute_irrad_correction(panle_folder_path, panel_img_name, bounding_box)

### Step 2 - DLS correction of variable irradiance images - Method 1
input_path=r'.\Example Dataset\Micasense Images'  ## Insert the main folder that contains all the Micasense image folders (000, 001, 002, etc.)
corrected_path= r'.\Example Dataset\DLS Corrected-Method 1'  ## Insert output folder path where all the processed images will be stored

if not os.path.exists(corrected_path):
    os.makedirs(corrected_path)
Parallel(n_jobs=8, prefer= 'threads')(delayed(DLS_correction)(SI, corrected_path, panel_corr) for SI in glob.glob(input_path+'\*\*.tif'))
for or_files in glob.glob(corrected_path+'\*_original'):  
    os.remove(or_files)     

### Step 3 - Irradiance proximity based reflectance calibration - Method 2 

## Create a separate folder to store images of the in-field calibration targets. This code requires that each target has a dedicated folder for itself. 
## Example: all images of target 1 are saved in a folder named 'Target 1', and so on. 
target_folders_path=r'.\Example Dataset\Targets'
metadata_path=r'.\Example Dataset\Metadata'
##Extract all metadata from the target images 
data_type='T'
bounding_box=20 ##Change this as needed
metadata_extract(target_folders_path, metadata_path, data_type, bounding_box)

## Populate the colum 'Actual reflectance' in the outpust spreadsheet with the target metadata. 


##Extract all metadata from the all corrected images
data_type='NT'
metadata_extract(corrected_path, metadata_path, data_type)

##Perform linear regression (emperical line method aka ELM) of the target actual vs estimated reflectance
##Choose calib_method 'OELM' for object-based ELM (default) or 'FSELM' for full-scale ELM
##You can modify the calibration method as needed in the script 
calib_method='OELM' #or 'FSELM'
target_liner_regression( metadata_path, calib_method)

## Assign a target to each image based on irradiance proximity
## NEarest neighbor algorithm was used to assign reflectance calibraion targets
irradiance_proximity_matching(metadata_path)
irrad_prox_list=combine_irrad_proximity_list(metadata_path)

##Perform irradiance proximity based image calibration 
calibrated_path= r'.\Example Dataset\DLS Calibrated-Method 2'
if not os.path.exists(calibrated_path):
    os.makedirs(calibrated_path)
Parallel(n_jobs=8, prefer= 'threads')(delayed(DLS_proximity_calibration)(SI, calibrated_path, irrad_prox_list) for SI in glob.glob(calibrated_path[0:-1]+'*.tif'))
for or_files in glob.glob(calibrated_path+'\*_original'):  
    os.remove(or_files)   

###If using Altum or higher - Insert code to copy Thermal band images from the original folder to the newly created folder. 

###Process the output images with Agisoft metashape or any other photogrammetric image processing software 