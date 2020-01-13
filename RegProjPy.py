# RegProjPy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('uber_nyc_enriched.csv')

# visualizing missing data in the dataset
sns.heatmap(df.isnull(), cbar=False, cmap="YlGnBu_r")
plt.show()

# removing n/a and non borough values
df = df[(df.borough != 'EWR')].dropna(how='any', axis=0) # drop airport and nan values

# compressing all the hourly datapoints into daily datapoints for the final df
edfList = [] # list with every row of data to be in the final df
for day in df.pickup_dt.str.slice(0,10).unique():
    for bur in df.borough.unique():
        # creating a df for each day by borough
        daydf = df[(df.pickup_dt.str.slice(0,10) == day) & (df.borough == bur)]
        # calculating averages and values for daily values
        daylist = [day, bur, np.sum(daydf.pickups), np.mean(daydf.spd),
                    np.mean(daydf.vsb), np.mean(daydf.temp), np.mean(daydf.dewp),
                    np.mean(daydf.slp), list(daydf.pcp24)[-1], np.mean(daydf.sd),
                    list(daydf.hday)[0]]
        edfList.append(daylist)

# creating the final dataframe that we will write to .csv
edf = pd.DataFrame(edfList, columns=df.columns.drop(['pcp06','pcp01'])).rename(columns={'pcp24':'pcp'})

# adding weekends into edf
weekendList = []
for i in range(0,905,5):
    if i == 10 or (i%35) == 10 or i == 15 or (i%35) == 15:
        for i in range(5):
            weekendList.append('Y')
    else:
        for i in range(5):
            weekendList.append('N')
edf['weekend'] = weekendList

# creating column of dummy variable for dayType
dayType = []
for i in range(0,edf.shape[0]):
    if edf.hday[i] == 'Y' and edf.weekend[i] == 'Y':
        dayType.append('WendHday')
    elif edf.hday[i] == 'Y' and edf.weekend[i] == 'N':
        dayType.append('Hday')
    elif edf.hday[i] == 'N' and edf.weekend[i] == 'Y':
        dayType.append('Wend')
    elif edf.hday[i] == 'N' and edf.weekend[i] == 'N':
        dayType.append('Wday')
edf['dayType'] = dayType

# dropping interim columns from dayType calculations
edf = edf.drop(['hday','weekend'], axis = 1)

# adding column for qualitative month
edf['month'] = edf.pickup_dt.str.slice(5,7).replace({'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun'})

# writing the final edf to .csv , purposely wont overwrite existing .csv
try:
    pd.read_csv('uber_nyc_clean.csv')
    print('uber_nyc_clean.csv already exists. Exiting RegProjPy')
except:
    edf.to_csv('uber_nyc_clean.csv')
