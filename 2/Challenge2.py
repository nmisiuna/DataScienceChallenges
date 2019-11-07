# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
pd.options.display.max_columns = 500
import matploglib.pypplot as plt

#Read in data
data = pd.read_csv('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\2\\ad_table.csv')

#Pre-process
data['date'] = pd.to_datetime(data['date'], format = '%Y-%m-%d')
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
