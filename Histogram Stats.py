# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 20:08:57 2023

@author: Vaishali.Swaminathan
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.distance import correlation, euclidean,jensenshannon
from scipy.stats import ks_2samp, pearsonr,gaussian_kde,chisquare, entropy
from math import log, e
# from statsmodels.graphics.gofplots import qqplot_2samples
import matplotlib


def get_density(x, cov_factor=0.1):
        #Produces a continuous density function for the data in 'x'. Some benefit may be gained from adjusting the cov_factor.
        density = gaussian_kde(x)
        density.covariance_factor = lambda:cov_factor
        density._compute_covariance()
        return density
# from scipy.stats import bhattacharyya
# Load the first Excel file into a pandas DataFrame and extract the values from the desired column
file_path=r'Example Dataset\Histogram analysis\Histogramss.xlsx'

file_name = pd.ExcelFile(file_path)
sheets= file_name.sheet_names

fig= plt.figure()
spec = matplotlib.gridspec.GridSpec(ncols=5, nrows=5)
ax=[]
for i in range(20):
    if i%4==0: ##only first column
        if i/4<1: #first box
            ax.append(fig.add_subplot(spec[int(i/4), i%4:i%4+2]))
        else:
            if i/4>=1:
                ax.append(fig.add_subplot(spec[int(i/4), i%4:i%4+2], sharex= ax[0])) 
    else: #other columns 
        if i%4==1:
            ax.append(fig.add_subplot(spec[int(i/4), i%4+1:i%4+2]))
        elif i%4>1:
            ax.append(fig.add_subplot(spec[int(i/4), i%4+1:i%4+2]))#, sharey=ax[i+1-i%4]))
# ax1= fig.add_subplot(spec[0, 0:2])
# ax2= fig.add_subplot(spec[0, 2:4], sharey=ax1)
# ax3= fig.add_subplot(spec[0, 4:6],sharey=ax1)
# ax4= fig.add_subplot(spec[1, 1:3], sharey=ax1)
# ax5= fig.add_subplot(spec[1, 3:5],sharey=ax1)
plt.setp(ax[2].get_yticklabels(), visible=False)
plt.setp(ax[3].get_yticklabels(), visible=False)
plt.setp(ax[6].get_yticklabels(), visible=False)
plt.setp(ax[7].get_yticklabels(), visible=False)
plt.setp(ax[10].get_yticklabels(), visible=False)
plt.setp(ax[11].get_yticklabels(), visible=False)
plt.setp(ax[14].get_yticklabels(), visible=False)
plt.setp(ax[15].get_yticklabels(), visible=False)
plt.setp(ax[18].get_yticklabels(), visible=False)
plt.setp(ax[19].get_yticklabels(), visible=False)

plt.setp(ax[0].get_xticklabels(), visible=False)
plt.setp(ax[1].get_xticklabels(), visible=False)
plt.setp(ax[2].get_xticklabels(), visible=False)
plt.setp(ax[3].get_xticklabels(), visible=False)
plt.setp(ax[4].get_xticklabels(), visible=False)
plt.setp(ax[5].get_xticklabels(), visible=False)
plt.setp(ax[6].get_xticklabels(), visible=False)
plt.setp(ax[7].get_xticklabels(), visible=False)
plt.setp(ax[8].get_xticklabels(), visible=False)
plt.setp(ax[9].get_xticklabels(), visible=False)
plt.setp(ax[10].get_xticklabels(), visible=False)
plt.setp(ax[11].get_xticklabels(), visible=False)
plt.setp(ax[12].get_xticklabels(), visible=False)
plt.setp(ax[13].get_xticklabels(), visible=False)
plt.setp(ax[14].get_xticklabels(), visible=False)
plt.setp(ax[15].get_xticklabels(), visible=False)
# ax1.set_ylabel('Exposure time (ms)',fontsize=16)
# ax4.set_ylabel('Exposure time (ms)',fontsize=16)
ax[0].set_title('Reflectance Histogram',y= 1.055, fontsize=14,fontweight='bold')
ax[1].set_title('Conventional*',y= 1.055, fontsize=14,fontweight='bold')
ax[2].set_title('Q-Q plots\n\nMethod 1*',y= 1.055, fontsize=14,fontweight='bold')
ax[3].set_title('Method 2*',y= 1.055, fontsize=14,fontweight='bold')


# fig, ax = plt.subplots(5,4, sharey=True)#, sharey=True)
# ax = ax.flatten()
c=1
X= ['16June2021_CRP+DLS-Calibrated-Pixel Freq',	'16June2021_Method1-Pixel Freq',	 '16June2021_Method2-Pixel Freq']
labels=['A', 'B','C', 'D', 'E', 'F', 'G','H', 'I', 'J', 'K', 'L','M', 'N', 'O']
li=0
for sht in sheets:
    m=1
    df = pd.read_excel(file_name, sheet_name=sht)
    values1 = df['17June2021_ClearSky-Calibrated-Pixel Freq'].replace(np.nan,0).values[101:201]
    values1=values1/100000
    refl=df['Reflectance'].replace(np.nan,0).values[101:201]   #Ignoring reflectance < 0
    ax[c-m].plot( refl,values1, label='Clear Sky*')
    ##Intersection for reference 
    ref=0
    for f in range(len(values1)):
        ref+=min(values1[f],values1[f])
    for x in X:
        values2 = df[x].replace(np.nan,0).values[101:201]
        values2=values2/100000
        ##Get quantile Q-Q plot
        q1=[]; q2=[]
        for i in range(0,100):
            q1.append(np.quantile(values1, i/100))
            q2.append(np.quantile(values2, i/100))
        # Calculate the histograms of the two datasets
        labl=x.split('_')[1].split('-')[0].replace('CRP+DLS','Conventional')
        ax[c-m].plot(refl,values2,  label=labl+'*')
        
        ax[c-m].set_ylabel(sht, fontsize=12,fontweight='bold')
        ax[c-m].legend(loc='upper right')
        ax[c-m].set_aspect('auto')
        

        # # Calculate the correlation between the two histograms
        corr = correlation(values1, values2)
        corr_pear=pearsonr(values1, values2)
     
        # Calculate the Bhattacharyya distance between the two histograms
        #Get density functions:
        d1 = get_density(values1)
        d2 = get_density(values2)
        dv1=[d1(i)for i in range(len(refl))]
        dv2=[d2(i)for i in range(len(refl))]
        cX = np.concatenate((values1, values2))
        bins = len(refl) - 1
        bc=0
        for i in range(bins):
            # bc += (max(cX)-min(cX))*np.sqrt(d1(i) * d2(i))/bins
            bc += np.sqrt(d1(i)* d2(i))
        db= -log(bc)
        
        ##Kullback–Leibler Divergence
        prob1=values1/np.sum(values1)
        prob2=values2/np.sum(values2)
        kl= entropy(prob1, prob2)
       
        # chi2=chisquare(values2,values1)
        js= jensenshannon(q2,q1)#, axis=0)
        kol_smir=ks_2samp(q2,q1)      #Kolmogorov-Smirnov-- valid for continuous distribution as in this case
        
        ## Determine intersection of curves
        intr=0
        for f in range(len(values2)):
            intr+=min(values1[f],values2[f])
        intr=intr/ref
        print("{} intersection={:.2f}   corr={:.2f}  db={:.2f}   ks={:.2f}   js={:.2f}   kl={:.2f}   pearson (p-val)={:.4f}   Kolmogorov-Smirnov (p-val)={:.2f}".format(labl,intr,corr_pear[0],db, kol_smir[0],js,kl,corr_pear[1],kol_smir[1]))
        
        
        
        
        ax[c].scatter(q1,q2)
        ax[c].plot([min(q1), max(q1)], [min(q1), max(q1)], color='black')
        ax[c].set_aspect('auto')
        ax[c].text(0.0,max(q1)-max(q1)/5, labels[li], fontsize=12, fontweight='bold')
        corr_pear=pearsonr(q1, q2)
        # print('{}: {:.2f}'.format(labl, corr_pear[0]))
        # qqplot_2samples(values1,values2, ax=ax[c])
        m+=1
        c+=1
        li+=1
    c+=1
    
ax[8].set_ylabel('Frequency (x$10^5$)\n\nRed', fontsize=14,fontweight='bold')
ax[16].set_xlabel('\nReflectance ratio',  fontsize=14,fontweight='bold')
ax[18].set_xlabel('\nFrequency (x$10^5$)', fontsize=14,fontweight='bold')
