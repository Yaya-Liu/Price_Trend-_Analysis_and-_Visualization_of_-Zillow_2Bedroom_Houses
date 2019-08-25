# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 13:16:52 2019

@author: Yaya Liu
"""

# Zillow Median Home Value Datasets - Column Level Metadata
#ZHVI 2 - Bedroom Time Series($)(by Zip code)

# Field Description
# RegionalID: Zillow assigned number only, assigned consecutively when the regions are defined
# RegionName: Zip code of where the propertey is located
# City: City of where the property is located
# State: State of where the property is located
# Metro: General name of the surrounding area where the property is located
# CountyName: Political and administrative division of a state, referred to as a particular part of the state
# SizeRank: Population of the area, the lower the number the greater the population
# 1996-04-XXXX-XX: indicates the historical median price within the area
# (XXXX-XX indicates the latest date available at the time the data is pulled) 



import pandas as pd
import numpy as np
import copy
import matplotlib.pyplot as plt
import os

if not os.path.exists("figs"):
    os.makedirs("figs")

url = "http://files.zillowstatic.com/research/public/Zip/Zip_Zhvi_2bedroom.csv"
df = pd.read_csv(url, encoding = "ISO-8859-1")
#print(df)

print(df.sample(10))
df.shape          #(9086, 286)
df.columns
df.dtypes

# count and drop rows within missing values.
df.isnull().sum()
df1 = df.dropna()
df1.isnull().sum()  
df1.shape  #(7742, 286), 1344 rows has been removed


col_to_counted = ['RegionName', 'City', 'State', 'Metro', 'CountyName']
for col in col_to_counted:
    print(df1[col].value_counts())

# Results:     
# RegionName, Length: 7742, dtype: int64
# City, Length: 4144, dtype: int64
# States, 48, dtype: int64 
# Metro, Length: 523, dtype: int64
# CountyName, Length: 706, dtype: int64

df_rise = copy.deepcopy(df1)

for col in df_rise.columns[7:]:
    df_rise[col] = df_rise[col].apply(lambda x: round(x/1000, 2))

df_rise.head(10)    


# Bar plot shows 5 cities with highest housing price in 05/2019
df_highest = df_rise.sort_values('2019-06', ascending = False)[0:5]
plt.bar(df_highest['City'], df_highest['2019-06'], width = 0.5)
plt.title("5 cities with highest housing price in June 2019")
plt.xlabel('City')
plt.ylabel('Average Price, in thousands')
plt.savefig("figs/" + '5CitiesWithHighestHousingPrice' + ".png", dpo = 100)
plt.show()

# Add new column: increasePercent, represents the increase percentage from '1996-04' to '2019-05' 
df_rise['increasePercent'] = (df_rise['2019-06'] - df_rise['1996-04'])/df_rise['1996-04'] * 100

# Scatter plot between size rank and increase in percentage
plt.scatter(df_rise['SizeRank'], df_rise['increasePercent'])
plt.xlabel('Size Rank')
plt.ylabel('Percentage increase from 1996/04 to 2019/05')
plt.show()

# histgrom shows the probability of the average increase rate over all states
df_rise_stateAgg = df_rise.groupby(['State']).mean()
df_rise_stateAgg = df_rise_stateAgg.sort_values('increasePercent', ascending = False)
x = df_rise_stateAgg['increasePercent']
#x.hist(bins = 10, xrot = 90)
x.hist(bins = 15)
plt.xlabel('Percentage increase from 1996/04 to 2019/05')
plt.ylabel('Probability')
plt.show()

# Line chart shows top 5 states have the largest increase rate from 1996/04 - 2019/05 (by month)
topStates = 5
df_rise_stateAgg_T = df_rise_stateAgg.iloc[0:topStates,3:-1].T
#plt.figure(figsize = (16, 10))
df_rise_stateAgg_T.plot(title = str(topStates) + " States with Largest Increase from 1996/04 to 2019/05", xticks = range(0, 1))
#df_rise_stateAgg_T.plot(title = "10 States with Largest Increase from 1996/04 to 2019/06")
plt.legend(title = "State", bbox_to_anchor=(1, 1))
#plt.xticks(np.arange(0, 100, step=10), np.arange(0, 100, step=10), rotation = 25)
plt.grid(True)
plt.xlabel('By  Month')
plt.ylabel('Average Price, in thousands')
plt.show()

# Line chart shows top 5 states have the largest increase rate from 1996/04 - 2019/05 (by year) 
df_rise_stateAgg_T.index
df_rise_stateAgg_T.reset_index(level = 0, inplace = True)    # reset index
df_rise_stateAgg_T['Year'] = df_rise_stateAgg_T['index'].apply(lambda x: x.split("-")[0])
df_rise_stateAgg_T['month'] = df_rise_stateAgg_T['index'].apply(lambda x: x.split("-")[1])

df_yearAgg = df_rise_stateAgg_T.groupby(['Year']).mean()
df_yearAgg.plot(title = str(topStates) + " States with Largest Increase from 1996 to 2019", xticks = range(0, len(df_yearAgg)))
plt.legend(title = "State", bbox_to_anchor=(1, 1))
plt.xticks(rotation = 90)
plt.grid(True)
plt.xlabel('By Year')
plt.ylabel('Average Price, in thousands')
plt.show()

# US states heatmap
import chart_studio.plotly as py
import chart_studio.tools as tls


df_rise_stateAgg.reset_index(level = 0, inplace = True) 

tls.set_credentials_file(username = 'cloverlyy', api_key = 'RsKQETjmHeHXwG8oM71w')

df_rise_stateAgg['Text'] = '' #'States' + df_rise_stateAgg['State'] + '<br>' + 'Average Price' + df_rise_stateAgg['2019-05'].astype(str)

data = [dict(type = 'choropleth', autocolorscale = False, locations = df_rise_stateAgg['State'], z = df_rise_stateAgg['2019-06'],\
             locationmode = 'USA-states', text = df_rise_stateAgg['Text'], colorscale = 'Portland',\
             colorbar = dict(title = 'Average Housing Price'))]
    
layout = dict(title = "2-Bedroom Average Housing Price in June 2019, in thousands", geo = dict(scope = 'usa', projection = dict(type = 'albers usa')))

fig = dict(data = data, layout = layout)

py.plot(fig, filename = "Housing Price")



