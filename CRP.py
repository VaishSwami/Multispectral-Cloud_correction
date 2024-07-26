# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 12:22:37 2024

@author: swami
"""
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 11:01:22 2021

@author: vaishaliswaminathan
"""


import numpy as np
import skimage.color
import skimage.io
import skimage.viewer
from matplotlib import pyplot as plt
import micasense.image as image
import micasense.panel as panel
import micasense.metadata as metadata
import micasense.utils as msutils
import micasense.dls as dls
import datetime, pytz, imageio, os, cv2, glob, math
from math import pi
from micasense import plotutils

exiftoolPath=os.path.normpath(os.environ.get('exiftoolpath'))


def compute_irrad_correction(panel_image_folder_path, image_name, box_size=20):
    corr_fact=[]
    if '.tif' in image_name:
        image_name=image_name[:-4]
    for panelimg in glob.glob(panel_image_folder_path+'\\'+image_name+'_*'+'.tif'):
        panelraw= skimage.io.imread(panelimg)
        
        panelmeta = metadata.Metadata(panelimg, exiftoolPath=exiftoolPath)  ##reading panel image metadata
        bandName = panelmeta.get_item('XMP:BandName')  
        panel_incident= panelmeta.get_item('XMP:Irradiance')
        # dls_orientation_vector = np.array([0,0,-1])
        # dir_dif_ratio=6.0
        panelrad=msutils.raw_image_to_radiance(panelmeta,panelraw)[0]
        coord=np.zeros((3,2),np.int)
        
        def click_event(event, x, y, flags, params):
            counter=0
            if event == cv2.EVENT_LBUTTONDOWN:
                coord[counter]=int(x),int(y)
                counter+=1
                
        cv2.imshow('select center x,y', panelraw)
        cv2.setMouseCallback('select center x,y', click_event)
        cv2.waitKey(0)
        cv2.destroyWindow('select center x,y')
        x1=coord[0][0]; y1=coord[0][1]

        z=box_size   
        ulx=x1-z ;uly=y1+z ;lrx=x1+z ; lry= y1-z #black panel
        
        cv2.rectangle(panelrad,(ulx,uly),(lrx,lry),(0,255,0),3)
        panelCalibration = { 
            "Blue": 0.5344, 
            "Green": 0.5346, 
            "Red": 0.5331, 
            "Red edge": 0.5319, 
            "NIR": 0.5293 
        }
        panelRegion= panelrad[lry:uly, ulx:lrx]
        plotutils.plotwithcolorbar(panelrad, 'Panel region in radiance image')
        meanRadiance = panelRegion.mean()
        
        ##corr fact for radiance image
        corr= panelCalibration[bandName]/meanRadiance
        corr_fact.append(corr)
        
    return corr_fact
    
