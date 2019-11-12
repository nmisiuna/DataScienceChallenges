# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
pd.options.display.max_columns = 500
import matplotlib.pyplot as plt
import sklearn.linear_model as lm
import numpy as np
from statsmodels.tsa.arima_model import ARIMA

from pandas.plotting import autocorrelation_plot

#Read in data
data = pd.read_csv('C:\\Users\\s0159480\\Documents\\GitHub\\DataScienceChallenges\\2\\ad_table.csv')

#Pre-process
data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d')
data.sort_values('date', inplace = True)
data['date_as_day'] = data['date'].dt.dayofyear
data['total_cost_per_click'] = data['avg_cost_per_click'] * data['clicked']

#Look at the different ad groups
adGroupsAgg = data.groupby('ad').agg(['mean', 'sum'])

#Identify the 5 best ad groups
#This can be done in a few different wants
#1. Total revenue / click cost
#
print((adGroupsAgg['total_revenue']['sum'] / 
       adGroupsAgg['total_cost_per_click']['sum']).sort_values(ascending = False)[:5])

#Now predict through december
plt.figure(figsize = (10, 10))
for group in data['ad'].unique():
    df = data.loc[data['ad'] == group, :]
    plt.plot(df['date'], df['shown'].cumsum())
    plt.xticks(rotation = -30)
plt.show()

line = lm.LinearRegression()
line.fit(data['date_as_day'].values.reshape(-1, 1), 
         data['shown'].cumsum().values.reshape(-1, 1))
yPred = line.predict(np.arange(327, 365, 1).reshape(-1, 1))
plt.figure(figsize = (10, 10))

#Plot original plus prediction
plt.plot(np.append(data['date_as_day'], np.arange(327, 365)).reshape(-1, 1),
         np.append(data['shown'].cumsum(), yPred))
plt.xticks(rotation = -30)
plt.show()

#Now I really need to do this for each of the groups
plt.figure(figsize = (10, 10))
plt.xticks(rotation = -30) 
for group in data['ad'].unique():
    df = data.loc[data['ad'] == group, :]
    line = lm.LinearRegression()
    line.fit(df['date_as_day'].values.reshape(-1, 1), 
             df['shown'].cumsum().values.reshape(-1, 1))
    yPred = line.predict(np.arange(327, 365, 1).reshape(-1, 1))    
    #Plot original plus prediction
    plt.plot(np.append(df['date_as_day'], np.arange(327, 365)),
             np.append(df['shown'].cumsum(), yPred))
    
    #If we only want the specific date it said
#    yPred = line.predict(np.array([pd.Timestamp(2015, 12, 15, 0, 0).dayofyear, pd.Timestamp(2015, 11, 24, 0, 0).dayofyear]).reshape(-1, 1))
    yPred = line.predict(np.array([pd.Timestamp(2015, 12, 15, 0, 0).dayofyear, pd.Timestamp(2015, 12, 14, 0, 0).dayofyear]).reshape(-1, 1))
    print(group + ': ' + str(yPred[0, 0] - yPred[1, 0]))

plt.show()

#Want to find if avg_cost_per_click is down/up/flat
#Just fit a line and look at coefficient
groupCoef = {}
plt.figure(figsize = (10, 10))
plt.xticks(rotation = -30)
for group in data['ad'].unique():
    df = data.loc[data['ad'] == group, :]
    plt.plot(df['date'], df['avg_cost_per_click'])
    line = lm.LinearRegression()
    line.fit(df['date_as_day'].values.reshape(-1, 1),
             df['avg_cost_per_click'].values.reshape(-1, 1))
    groupCoef[group] = line.coef_[0, 0]
    
plt.show()

#Now cluster on coef
#First let's just look at it
plt.figure(figsize = (10, 10))
plt.xticks(rotation = -30)
#plt.scatter(groupCoef.values(), [1 for i in range(len(groupCoef.values()))])
plt.scatter(groupCoef.values(), np.ones(len(groupCoef.values())))
plt.show()
#Looking at the figure, make a cut off at 0.004 for positive and -0.005 for negative
print('Increasing cost: ')
for j in [i for i in groupCoef.keys() if groupCoef[i] > 0.004]:
    print(j)
print('Decreasing cost: ')

for j in [i for i in groupCoef.keys() if groupCoef[i] < -0.005]:
    print(j)
print('Flat cost: ')
for j in [i for i in groupCoef.keys() if (groupCoef[i] > -0.005) and (groupCoef[i] < 0.004)]:
    print(j)
    
#Try k-means on the coefficients
from sklearn.cluster import KMeans
km = KMeans(3)
km.fit(np.array(list(groupCoef.values())).reshape(-1, 1))
#Now print each of the ad groups in each cluster

plt.figure(figsize = (10, 10))
plt.xticks(rotation = -30)
colorDict = {0: 'red', 1:'blue', 2:'green'}
for label in set(km.labels_):
    #Get indices
    print('Cluster: ' + str(label))
    print('Center: ' + str(km.cluster_centers_[label]))
    if (km.cluster_centers_[label] == min(km.cluster_centers_)):
        print('Decreasing')
    elif (km.cluster_centers_[label] == max(km.cluster_centers_)):
        print('Increasing')
    else:
        print('Flat')
    temp = [i for i in range(len(km.labels_)) if km.labels_[i] == label]
    z = [list(groupCoef.keys())[i] for i in temp]
    for i in z:
        print(i)
    plt.scatter([groupCoef[i] for i in z], np.ones(len(z)), color = colorDict[label])
plt.show()

#Plot the original coefficient scatter plot along with the cluster centers for 
#better visualization
plt.figure(figsize = (10, 10))
plt.xticks(rotation = -30)
#plt.scatter(groupCoef.values(), [1 for i in range(len(groupCoef.values()))])
plt.scatter(groupCoef.values(), np.ones(len(groupCoef.values())))
plt.scatter(km.cluster_centers_, np.ones(3), color = 'red')
plt.show()

#Now let's do an ARIMA model on shown
#I'm not doing any parameter tuning, which absolutely would help
for group in data['ad'].unique():
    df = data.loc[data['ad'] == group, :]
    df.set_index('date_as_day', inplace = True)
plt.figure(figsize = (10, 10))
autocorrelation_plot(df['shown'])
plt.show()

model = ARIMA(df['shown'], order = (5, 1, 0))
modelFit = model.fit(disp = 0)
residuals = pd.DataFrame(modelFit.resid)
residuals.plot(kind = 'kde')
plt.show() #Can see it's bi-modal, but mostly zero-mean

plt.figure(figsize = (10, 10))
modelFit.plot_predict(dynamic = False)
plt.show()
#This actually doesn't do half-bad!  It would probably suck if used
#to predict out to December, however
#Let's try that
fc, sc, conf = modelFit.forecast(pd.Timestamp(2015, 12, 15, 0, 0).dayofyear - df.index.max())
temp = range(df.index.max(), pd.Timestamp(2015, 12, 15, 0, 0).dayofyear)
fcSeries = pd.Series(fc, index = temp)
lowerSeries = pd.Series(conf[:, 0], index = temp)
upperSeries = pd.Series(conf[:, 1], index = temp)

plt.figure(figsize = (10, 10))
plt.plot(df['shown'], label = 'training')
plt.plot(fcSeries, label = 'forecast')
plt.fill_between(lowerSeries.index, lowerSeries, upperSeries, color = 'k', alpha = 0.15)
plt.title('Forecast')
plt.legend(loc = 'upper left')
plt.show()


#Try this for avg_cost_per_click
for group in data['ad'].unique():
    df = data.loc[data['ad'] == group, :]
plt.figure(figsize = (10, 10))
autocorrelation_plot(df['avg_cost_per_click'])
plt.show()

model = ARIMA(df['avg_cost_per_click'], order = (5, 1, 0))
modelFit = model.fit(disp = 0)
residuals = pd.DataFrame(modelFit.resid)
residuals.plot(kind = 'kde')
plt.show() #It's zero mean, so the residuals aren't terrible.  Not normally distributed, however

plt.figure(figsize = (10, 10))
modelFit.plot_predict(dynamic = False)
plt.show()
#This one, however, is garbage.