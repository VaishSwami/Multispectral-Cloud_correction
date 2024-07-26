# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 12:01:47 2024

@author: swami
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
import pandas as pd

exiftoolPath=os.path.normpath(os.environ.get('exiftoolpath'))

def img_conv_save(shadow_refl,reference_file,dest_path, output_name):    
    im = Image.fromarray(shadow_refl.astype(np.float32))     ###Changes this to floating point reflectance                    
    im.save(dest_path+'\\'+output_name)
    
    ##Copying metadata from original to new reflectance image
    cmd= '{} -TagsFromFile "{}" -XMP "{}"'.format(exiftoolPath,reference_file, dest_path+'\\'+output_name)
    subprocess.call(cmd)
    cmd= '{} -TagsFromFile "{}" -Composite "{}"'.format(exiftoolPath,reference_file, dest_path+'\\'+output_name)
    subprocess.call(cmd)


def DLS_correction(input_file, corrected_path, panel_corr ):
    shadow_image = skimage.io.imread(input_file, as_gray=True)    #variable name for shadow dataset
    shadow_meta = metadata.Metadata(input_file, exiftoolPath=exiftoolPath)
    shadow_incident= shadow_meta.get_item('XMP:Irradiance')
    band=shadow_meta.get_item('XMP:BandName')
    
    ##May be useful for images captured under non-solar noon or other atypical conditions
#    si_location=(shadow_meta.get_item('Composite:GPSLongitude'),shadow_meta.get_item('Composite:GPSLatitude'))
#    si_dls_pose=(float(shadow_meta.get_item('XMP:Yaw')),float(shadow_meta.get_item('XMP:Pitch')),float(shadow_meta.get_item('XMP:Roll')))
#    si_utc_time= datetime.datetime.strptime(shadow_meta.get_item('EXIF:CreateDate'), '%Y:%m:%d %H:%M:%S')
#    si_utc_time= pytz.utc.localize(si_utc_time)
    
#    dls_orientation_vector = np.array([0,0,-1])
#    (sun_vector_ned,    # Solar vector in North-East-Down coordinates
#    sensor_vector_ned, # DLS vector in North-East-Down coordinates
#    sun_sensor_angle,  # Angle between DLS vector and sun vector
#    solar_elevation,   # Elevation of the sun above the horizon
#    solar_azimuth,     # Azimuth (heading) of the sun
#    )= dls.compute_sun_angle(si_location,si_dls_pose,si_utc_time,dls_orientation_vector)
#    fresnel_coeff= dls.fresnel(sun_sensor_angle)
#    percent_dif=1/6.0
#    shadow_incident_cor= (shadow_incident*(percent_dif+np.sin(solar_elevation)))/(fresnel_coeff*(percent_dif+np.cos(sun_sensor_angle)))

    shadow_radianceImage= msutils.raw_image_to_radiance(shadow_meta, shadow_image)[0]
    shadow_refl=100*pi*shadow_radianceImage*panel_corr[int(input_file[-5])-1]/shadow_incident
    output_name= input_file.split("\\")[-1]
    img_conv_save(shadow_refl, input_file,corrected_path, output_name )


def DLS_proximity_calibration(corrected_file, calibrated_path, irrad_prox_list):

    input_file= corrected_file
    shadow_image = skimage.io.imread(input_file, as_gray=True)    #variable name for shadow dataset
    img_name =input_file.split("\\")[-1]
    
    row= irrad_prox_list.loc[irrad_prox_list['Image Name']== img_name]   # retrives the row corresponding to the image from the DF
    row_loc=row.index[row['Image Name']== img_name].tolist()[0]
    m = row['LR_Slope'][row_loc].astype(float); c = row['LR_Intercept'][row_loc].astype(float)
    prox_calib_img= shadow_image * m + c    # post processing calibration 
        
    output_name= img_name
    img_conv_save(prox_calib_img, input_file,calibrated_path, output_name )
    
    
    
    