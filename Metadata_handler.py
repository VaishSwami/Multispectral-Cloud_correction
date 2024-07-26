
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 17:50:29 2022

@author: Vaishali.Swaminathan
"""
import glob, shutil, os, skimage,timeit, random , cv2
import numpy as np
import pandas as pd
import skimage.io
import micasense.metadata as metadata
import subprocess
from joblib import Parallel, delayed
from sklearn.linear_model import LinearRegression
import statsmodels,os

exiftoolPath=os.path.normpath(os.environ.get('exiftoolpath'))

def metadata_extract(input_path, out_path, data_type,bounding_box=2 ):
    band_names={1:'Blue', 2:'Green',3:'Red',4:'NIR',5:'Red edge'}
    img_list=[[],[],[],[],[]]
    if data_type=='T':
        folder_path =input_path+'\*\*.tif'
    elif data_type== 'NT':
        folder_path = input_path+'\*.tif'
        
    for Img in glob.glob(folder_path):
        img_name= Img.split('\\')[-1]
        tarp_num= Img.split('\\')[-2]
        band_index= int(img_name.split('.')[0].split('_')[-1])-1
        meta = metadata.Metadata(Img, exiftoolPath=exiftoolPath)
        band=meta.get_item('XMP:BandName')
        exptime=meta.get_item('EXIF:ExposureTime')
        irrad= meta.get_item('XMP:Irradiance')
        gain=meta.get_item('EXIF:ISOSpeed')/100.0
        timestamp = meta.get_item('XMP:TimeStamp')
        lat= meta.get_item('EXIF:GPSLatitude')
        longi=meta.get_item('EXIF:GPSLongitude')
        
        if data_type=='T':
            panelraw= skimage.io.imread(Img)
            coord=np.zeros((3,2),np.int)
            
            counter=0
            def click_event(event, x, y, flags, params):
                nonlocal counter
                if event == cv2.EVENT_LBUTTONDOWN:
                    coord[counter]=int(x),int(y)
                    counter+=1
                    
            cv2.imshow('select center x,y of black, gray, and white targets (same order)', panelraw)
            cv2.setMouseCallback('select center x,y of black, gray, and white targets (same order)', click_event)
            cv2.waitKey(0)
            cv2.destroyWindow('select center x,y')
            x1=coord[0][0]; y1=coord[0][1]
            x2=coord[1][0]; y2=coord[1][1]
            x3=coord[2][0]; y3=coord[2][1]
            
            z=bounding_box   #window for bounding box
            ulx_b=x1-z ;uly_b=y1+z ;lrx_b=x1+z ; lry_b= y1-z #black panel
            ulx_g=x2-z ;uly_g=y2+z ;lrx_g=x2+z ; lry_g= y2-z #gray panel
            ulx_w=x3-z ;uly_w=y3+z ;lrx_w=x3+z ; lry_w= y3-z #white panel
            
            panelRegion_b= panelraw[lry_b:uly_b, ulx_b:lrx_b]
            panelRegion_g= panelraw[lry_g:uly_g, ulx_g:lrx_g]
            panelRegion_w= panelraw[lry_w:uly_w, ulx_w:lrx_w]
            
            cv2.rectangle(panelraw,(ulx_b,uly_b),(lrx_b,lry_b),(0,0,255),1)
            cv2.rectangle(panelraw,(ulx_g,uly_g),(lrx_g,lry_g),(0,0,255),1)
            cv2.rectangle(panelraw,(ulx_w,uly_w),(lrx_w,lry_w),(0,0,255),1)
            cv2.imshow( 'Panel region in radiance image',panelraw)
            cv2.waitKey(0)
            cv2.destroyWindow('Panel region in radiance image')
            
            meanRadiance_b = panelRegion_b.mean()
            meanRadiance_g = panelRegion_g.mean()
            meanRadiance_w = panelRegion_w.mean()
            
            col= [img_name, tarp_num,irrad, 'BLACK','', meanRadiance_b]
            img_list[band_index].append(col)
            col= [img_name, tarp_num,irrad, 'GRAY','', meanRadiance_g]
            img_list[band_index].append(col)
            col= [img_name, tarp_num,irrad, 'WHITE','', meanRadiance_w]
            img_list[band_index].append(col)
               
        elif data_type=='NT':
            row=[img_name, irrad, lat, longi,timestamp ]
            img_list[band_index].append(row)    
        
    if data_type=='T':
        for ind in range(5): 
            df= pd.DataFrame(img_list[ind], columns= [ 'Image Name', 'Target Number','Irradiance Value','Target Color','Actual reflectance', 'Image reflectance'])
            output_file_name= out_path+'\\Targets metadata.xlsx'
            if not os.path.exists(output_file_name):
              df.to_excel(output_file_name, sheet_name= band_names[ind+1])
                
            else:
                with pd.ExcelWriter(output_file_name,engine="openpyxl", mode='a') as fn:
                    df.to_excel(fn, sheet_name= band_names[ind+1])
                    fn.save()
    elif data_type=='NT':
        for ind in range(5): 
            df= pd.DataFrame(img_list[ind], columns= [ 'Image Name','Irradiance Value','Latitude','Longitude', 'Timestamp'])
            output_file_name= out_path+'\\All image metadata.xlsx'
            if not os.path.exists(output_file_name):
              df.to_excel(output_file_name, sheet_name= band_names[ind+1])
                
            else:
                with pd.ExcelWriter(output_file_name,engine="openpyxl", mode='a') as fn:
                    df.to_excel(fn, sheet_name= band_names[ind+1])
                    fn.save()
def target_liner_regression(file_path,calib_method='OELM'):
    sheetnames=pd.ExcelFile(file_path+'\\Targets metadata.xlsx').sheet_names
    
    for sheetname in sheetnames:
        data= pd.read_excel(file_path+'\\Targets metadata.xlsx', sheet_name=sheetname)
        df=pd.DataFrame(data)
        img_list=[]
        for i in range (0, len(df), 3):
            block= df[i:i+3]
            X={}; Y={}
            for j in range(i+3):
                X[df['Target Color'].values[j]]=df['Image reflectance'].values[j]
                Y[df['Target Color'].values[j]]=df['Actual reflectance'].values[j]
            Band= int(df['Image Name'].values[i].split('_')[-1].split('.')[0])
            x=[]; y=[]
            ##Change this based on the calibration for each date or calibration range preferred 
            if calib_method=='OELM':
                if Band ==1 or Band ==2 or Band ==3:
                    x.append(X['BLACK']);x.append(X['GRAY']);y.append(Y['BLACK']);y.append(Y['GRAY'])
                elif Band ==5:
                    x.append(X['BLACK']);x.append(X['GRAY']);x.append(X['WHITE']);y.append(Y['BLACK']);y.append(Y['GRAY']);y.append(Y['WHITE'])
                elif Band ==4:
                    x.append(X['GRAY']);x.append(X['WHITE']);y.append(Y['GRAY']);y.append(Y['WHITE'])
            elif calib_method =='FSELM':
                x.append(X['BLACK']);x.append(X['GRAY']);x.append(X['WHITE']);y.append(Y['BLACK']);y.append(Y['GRAY']);y.append(Y['WHITE'])
            x=np.array(x); y=np.array(y)
            LR_model= LinearRegression().fit(x.reshape((-1, 1)),y)
            m= LR_model.coef_[0]
            b= LR_model.intercept_
            # str_y= str(m)+'x'+str(b)
            row=[df['Image Name'].values[i], df['Target Number'].values[i],df['Irradiance Value'].values[i],m,b]
            img_list.append(row)
            
        df_out=pd.DataFrame(img_list, columns= ['Image Name', 'Target Number','Irradiance Value','LR_Slope', 'LR_Intercept'])
        output_file_name= file_path+'\\Individual Target Regression.xlsx'
        if not os.path.exists(output_file_name):
          df_out.to_excel(output_file_name, sheet_name= sheetname)
        
        else:
            with pd.ExcelWriter(output_file_name,engine="openpyxl", mode='a') as fn:
                df_out.to_excel(fn, sheet_name= sheetname)
                fn.save()

def closest_irrad(img, tarps):
    tarps = np.asarray(tarps)
    dist = (tarps - img)**2
    return np.argmin(dist)
def irradiance_proximity_matching(file_path):
    sheetnames=pd.ExcelFile(file_path+'\\Individual Target Regression.xlsx').sheet_names

    for sheetname in sheetnames:
        Tdf= pd.read_excel(file_path+'\\Individual Target Regression.xlsx', sheet_name=sheetname)
        Idf=pd.read_excel(file_path+'\\All image metadata.xlsx', sheet_name=sheetname)
        
        
        Tarps_irrad= Tdf['Irradiance Value'].astype(float)
        final_list=[]
        for i in range(len(Idf['Image Name'])):
            Img_irrad= Idf['Irradiance Value'][i].astype(float)
            tarp_loc=closest_irrad(Img_irrad, Tarps_irrad)
            j = tarp_loc
            
            row= [Idf['Image Name'][i],Idf['Irradiance Value'][i],Tdf['Image Name'][j],Tdf['Target Number'][j], Tdf['Irradiance Value'][j],Tdf['LR_Slope'][j],Tdf['LR_Intercept'][j]]
            final_list.append(row)
        
        
        df_out=pd.DataFrame(final_list, columns= ['Image Name', 'Image Irradiance Value','Target Name','Target Number','Target Irradiance Value','LR_Slope', 'LR_Intercept'])
        output_file_name= file_path+'\\Irradiance proximity calibration list.xlsx'
        if not os.path.exists(output_file_name):
          df_out.to_excel(output_file_name, sheet_name= sheetname)
        
        else:
            with pd.ExcelWriter(output_file_name,engine="openpyxl", mode='a') as fn:
                df_out.to_excel(fn, sheet_name= sheetname)
                fn.save()
def combine_irrad_proximity_list(file_path):    
    TdfB= pd.read_excel(file_path+'\\Irradiance proximity calibration list.xlsx', sheet_name='Blue')
    TdfG= pd.read_excel(file_path+'\\Irradiance proximity calibration list.xlsx', sheet_name='Green')
    TdfR= pd.read_excel(file_path+'\\Irradiance proximity calibration list.xlsx', sheet_name='Red')
    TdfRE= pd.read_excel(file_path+'\\Irradiance proximity calibration list.xlsx', sheet_name='Red edge')
    TdfNIR= pd.read_excel(file_path+'\\Irradiance proximity calibration list.xlsx', sheet_name='NIR')
    Tdf= pd.concat([TdfB, TdfG, TdfR, TdfRE, TdfNIR]) ## This is a master list with all the individual band metadata converted to one big table 
    return Tdf