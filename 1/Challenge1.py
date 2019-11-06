# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 10:15:38 2019

@author: s0159480
"""

import pandas as pd
pd.set_option('display.max_columns', 500)
import matplotlib.pyplot as plt
import numpy as np

indexUserID = lambda x: x.set_index('user_id', inplace = True)

home = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\home_page_table.csv')
indexUserID(home)
#user_id is unique and only appears once
#This makes this problem a LOT easier
paymentConf = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\payment_confirmation_table.csv')
indexUserID(paymentConf)
paymentPage = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\payment_page_table.csv')
indexUserID(paymentPage)
search = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\search_page_table.csv')
indexUserID(search)
user = pd.read_csv('C:\\Users\\s0159480\\Downloads\\Challenge1\\Funnel_Analysis\\user_table.csv')
indexUserID(user)
user['date'] = pd.to_datetime(user['date'], format = '%Y-%m-%d')

#I'm assuming all other tables only contain new users
#Otherwise I'd have to join on home to clean out other types of users
#Let's check this: search.index.isin(home.index).sum() Confirms we're good to go

#First want to paint a picture of the conversion rate
#Let's break it down by device, sex, and then plot it over time by date
#device
paymentConfDet = paymentConf.join(user, how = 'inner')
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
df['Home > Search'] = [sum(home.index.isin(search.index)),
  sum(~home.index.isin(search.index))]
df.index = ['Converted', 'Did not convert']
df['Search > Payment Page'] = [sum(search.index.isin(paymentPage.index)),
  sum(~search.index.isin(paymentPage.index))]
df['Payment Page > Payment Conf'] = [sum(paymentPage.index.isin(paymentConf.index)),
  sum(~paymentPage.index.isin(paymentConf.index))]
#This shows a precipitous drop off from the search to payment page.
#Half of users make it to search page
#13% of users on search page make it to payment page
#8% of users on payment page make it to payment confirmation page
#Let's break this down by device
def ConvRateTable(home, search, paymentPage, paymentConf):
    #I really should set up a loop for this instead of hard coding all three parts
    df = pd.DataFrame()
    df['Home > Search'] = [sum(home.index.isin(search.index)),
      sum(~home.index.isin(search.index)),
      sum(home.index.isin(search.index))  * 100.0 / home.shape[0]]
    df.index = ['Converted', 'Did not convert', 'Ratio Convert']
    df['Search > Payment Page'] = [sum(search.index.isin(paymentPage.index)),
      sum(~search.index.isin(paymentPage.index)),
      sum(search.index.isin(paymentPage.index)) * 100.0 / search.shape[0]]
    df['Payment Page > Payment Conf'] = [sum(paymentPage.index.isin(paymentConf.index)),
      sum(~paymentPage.index.isin(paymentConf.index)),
      sum(paymentPage.index.isin(paymentConf.index)) * 100.0 / paymentPage.shape[0]]
    return(df)
    
print(ConvRateTable(home, search, paymentPage, paymentConf))

def SepDevice(df, typ):
    return(df[df.join(user)['device'] == typ])
    
for i in ['Mobile', 'Desktop']: #This should really be something like i in user['device'].unique()
    print(i + ' only:')
    print(ConvRateTable(SepDevice(home, i),
                        SepDevice(search, i),
                        SepDevice(paymentPage, i),
                        SepDevice(paymentConf, i)))
#Mobile has a much higher conversion rate than desktop but still faces the same issues
#They should really focus on the mobile market
    
#The final task would be to break this down by page conversion rate by date
#To see if the date change is specifically due to one page's conversion rate
#home conversion rate over time

df = home[home.index.isin(search.index)].join(user)
LinePlot(df['date'].sort_values(), range(df.shape[0]),
         'Date', 'Cumulative Conversion', 'Home > Search Conversion Rates')
#Can see a marked difference occurring on that date

df = search[search.index.isin(paymentPage.index)].join(user)
LinePlot(df['date'].sort_values(), range(df.shape[0]),
         'Date', 'Cumulative Conversion', 'Search > Payment Page Conversion Rates')
#This one shows that the search to payment conversion rate is the one that took a HUGE hit

df = paymentPage[paymentPage.index.isin(paymentConf.index)].join(user)
LinePlot(df['date'].sort_values(), range(df.shape[0]),
         'Date', 'Cumulative Conversion', 'Payment Page > Payment Conf Conversion Rates')

#So I'd say the home page is still doing fine at getting people to the search page
#The search page > payment page and payment page > payment conf rates are terrible now
#Let's do this by device
#Copy/pasting 'cus I'm lazy. Should functionalize this
for i in ['Mobile', 'Desktop']:
    df = home[home.index.isin(search.index)].join(user)
    df = df.loc[df['device'] == i, :]
    LinePlot(df['date'].sort_values(), range(df.shape[0]),
             'Date', 'Cumulative Conversion', i + ' Home > Search Conversion Rates')
    #Can see a marked difference occurring on that date
    
    df = search[search.index.isin(paymentPage.index)].join(user)
    df = df.loc[df['device'] == i, :]
    LinePlot(df['date'].sort_values(), range(df.shape[0]),
             'Date', 'Cumulative Conversion', i + ' Search > Payment Page Conversion Rates')
    #This one shows that the search to payment conversion rate is the one that took a HUGE hit
    
    df = paymentPage[paymentPage.index.isin(paymentConf.index)].join(user)
    df = df.loc[df['device'] == i, :]
    LinePlot(df['date'].sort_values(), range(df.shape[0]),
             'Date', 'Cumulative Conversion', i + ' Payment Page > Payment Conf Conversion Rates')
#Insights: Desktop home to search conversion rate is phenomenal
#Mobile search home to search conversion rate needs help
#All struggle equally for the other 2 conversion steps
    
#This paints enough of a picture but I wouldn't present it like this
#I'd aggregate all/mobile/desktop plots into a single plot per step (3 figures, 3 lines per figure)
#This would much better highlight the differences
#I'd then do it the other way, combining the 3 steps per all/mobile/desktop
#to try to highlight the impact of each step and how home to search isn't bad