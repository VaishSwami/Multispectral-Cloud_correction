# Multispectral-Cloud_correction
Here we provide the codes to correct and calibrate Micasense multispectral images affected by moving cloud cover that result in variability in irradiance during data collection. The irradiance measurements from an on-board downwelling light sensor (DLS) is integrated into the image processing workflow to compute instantaneous irradiance. Then calibration is performed based on irradiance proximity, implemented with the nearest neighbor algirithm. 

Cite data, methods, and code as: Swaminathan, Vaishali, et al. "Radiometric Calibration of Uav Images Under Changing Illumination Conditions with a Downwelling Light Sensor (Dls)." Available at SSRN 4746333.

Read comments in main.py to edit file path and modify input parameters

You may request for sample data and examples using the link: https://drive.google.com/drive/folders/1wk_DCkDjKK9nbuSB14qngAAuQdkgS64m?usp=drive_link

Note: Follow Micasense tutorial and Github repository for package installation guidelines (https://micasense.github.io/imageprocessing/index.html)
