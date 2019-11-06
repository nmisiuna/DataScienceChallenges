# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 10:15:38 2019

@author: s0159480
"""

import pandas as pd
pd.set_option('display.max_columns', 500)
import matplotlib.pyplot as plt
import numpy as np

home = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\home_page_table.csv')
#user_id is unique and only appears once
#This makes this problem a LOT easier
paymentConf = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\payment_confirmation_table.csv')
paymentPage = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\payment_page_table.csv')
search = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\search_page_table.csv')
user = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\user_table.csv')
user['date'] = pd.to_datetime(user['date'], format = '%Y-%m-%d')

#First want to paint a picture of the conversion rate
#Let's break it down by device, sex, and then plot it over time by date
#device
paymentConfDet = paymentConf.set_index('user_id').join(user.set_index('user_id'), how = 'inner')
paymentConfDet['device'].value_counts() #2/3 of confirmed users are on mobile
paymentConfDet['sex'].value_counts() #it's almost equally split between genders. don't care about gender for now


def LinePlot(xData, yData, xLabel, yLabel, title):
    plt.plot(xData, yData)
    plt.xticks(rotation = -30)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()

LinePlot(paymentConfDet['date'].sort_values(), range(paymentConfDet.shape[0]),
         'Date', 'Cumulative Conversions', 'Conversions Over Time')

#This shows us that somewhere around 2015-03-01 the number of conversions a day
#began dropping significantly
#Let's break it down by device
for i in ['Desktop', 'Mobile']:
    LinePlot(paymentConfDet.loc[paymentConfDet['device'] == i, 'date'].sort_values(), 
             range(sum(paymentConfDet['device'] == i)),
             'Date', 'Cumulative Conversions', i + ' Conversions Over Time')
#This show it impacted them equally
#Therefore, we probably need to break it down by conversion rates as they occur
#from each step: home > search > payment > confirmation
#I want a couple of counts:
#1. Number of user_id in home but not in search
#2. Number of user_id in search but not in paymentPage
#3. Number of user_id in paymentPage but not in paymentConf
df = pd.DataFrame()
df['Home > Search'] = [sum(home['user_id'].isin(search['user_id'])),
  sum(~home['user_id'].isin(search['user_id']))]
df.index = ['Converted', 'Did not convert']
df['Search > Payment Page'] = [sum(search['user_id'].isin(paymentPage['user_id'])),
  sum(~search['user_id'].isin(paymentPage['user_id']))]
df['Payment Page > Payment Conf'] = [sum(paymentPage['user_id'].isin(paymentConf['user_id'])),
  sum(~paymentPage['user_id'].isin(paymentConf['user_id']))]
#This shows a precipitous drop off from the search to payment page.
#Half of users make it to search page
#13% of users on search page make it to payment page
#8% of users on payment page make it to payment confirmation page
#Let's break this down by device
def ConvRateTable(home, search, paymentPage, paymentConf):
    df = pd.DataFrame()
    df['Home > Search'] = [sum(home['user_id'].isin(search['user_id'])),
      sum(~home['user_id'].isin(search['user_id']))]
    df.index = ['Converted', 'Did not convert']
    df['Search > Payment Page'] = [sum(search['user_id'].isin(paymentPage['user_id'])),
      sum(~search['user_id'].isin(paymentPage['user_id']))]
    df['Payment Page > Payment Conf'] = [sum(paymentPage['user_id'].isin(paymentConf['user_id'])),
      sum(~paymentPage['user_id'].isin(paymentConf['user_id']))]
    return(df)
    
ConvRateTable()