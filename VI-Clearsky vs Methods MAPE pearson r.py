# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 16:57:54 2024

@author: Vaishali.Swaminathan
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 18:02:03 2024

@author: Vaishali.Swaminathan
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 15:35:39 2024

@author: Vaishali.Swaminathan
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
# from sklearn.metrics import mean_absolute_percentage_error as mape
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score
# import statsmodels.api as sm
import os, itertools
import matplotlib.pyplot as plt
from scipy.stats import linregress
from math import sqrt
import seaborn as sns


input_file = r'G:\My Drive\Prelims and Dissertation\Papers\Radiometric Calibration\Additional Analysis\VI\Shadow Zones\OutputIndex\Copy of Vegetation Index-reorg-Resaved-check and merge.xlsx'
cols=['CRP+DLS*',	'Method 1*','Method 2*']
# cols=['75 m - FE CRP+DLS*',	'75 m - FE Method 1*','75 m - FE Method 2*','75 m - AE CRP+DLS*','75 m - AE Method 1*','75 m - AE Method 2*']
fig = plt.figure()
plt= fig.add_subplot(111)
# i=0
plt2=plt.twinx()
sht='MAPE'
datafr = pd.read_excel(input_file, sheet_name=sht)
sht2='r'
datafr2 = pd.read_excel(input_file, sheet_name=sht2)
# plt.bar(datafr['MAPE']-0.25, datafr['30 m - FE CRP+DLS*'],width=0.1, color='blue',alpha=0.5, align='center', label='MAPE ('+col.split('- ')[-1]+')')
k=-0.3
colors=['orangered', 'deepskyblue','rebeccapurple']
for col,cl in zip(cols,colors):
    print(col)
    plt.bar(datafr['MAPE']+k, datafr[col],width=0.2, color=cl,alpha=0.6, align='center', label='MAPE ('+col.split('- ')[-1]+')')
    plt2.scatter(datafr2['Pearson r']+k, datafr2[col], color=cl,edgecolors='black', s=110,label='R\xb2 ('+col.split('- ')[-1]+')')
    k+=0.2
# ax[i].bar(datafr['RMSE'], datafr[2021],width=0.2, color='olive',alpha=0.5,align='center', label='RMSE (2021)')
# ax[i].bar(datafr['RMSE']+0.2, datafr[2022],width=0.2, color='brown',alpha=0.5,align='center', label='RMSE (2022)')
plt.set_ylabel('MAPE', fontsize=14, weight='bold')
# plt.legend(loc='upper left',ncols=len(cols), fontsize=10)
# ax[i].set_ylim(0,44)
sht='r'
datafr = pd.read_excel(input_file, sheet_name=sht)


plt2.set_ylim(0.3,1.03)
# # axt.set_xlim(-1,6)
plt2.set_ylabel('Pearson\'s r', rotation=270, va='bottom', fontsize=14,weight='bold')
plt2.set_xticks([-0.080,1,2,3,4,5,6],['NDRE','NDVI','GNDVI','TGI','CIrededge','CIgreen', 'RDVI'])
plt2.tick_params(labelsize=13)
plt.tick_params(labelsize=13)
# plt2.set_xticklabels(['Blue','Green','Red','Red edge','NIR'],fontsize=18)
# plt2.tick_params(axis='y', Labelsize=13)
# plt.set_yticklabels(fontsize=13)
# fig.setp(plt.get_xticklabels(), fontsize=50)
# plt2.tick_params(axis='x', Labelsize=13, weight='bold')
fig.legend(loc='lower center', ncols=6, fontsize=13)
# fig.suptitle((0.5, 0.90),'30 m AGL')

