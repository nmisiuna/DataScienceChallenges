# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 09:57:09 2019

@author: Nick
"""

import json
import pandas as pd
pd.options.display.max_columns = 500

#Read it in as a raw json
#with open('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\4\\song.json', 'r') as file:
#    data = json.load(file)
    
#This is gross.  Let's try pandas
data = pd.read_json('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\4\\song.json')
#Much better

#Top 3 states by number of users
print('Top three states: ')
print(data[['user_id', 'user_state']].groupby('user_state').agg('count').sort_values('user_id', ascending = False)[1:4])
print('Bottom three states: ')
print(data[['user_id', 'user_state']].groupby('user_state').agg('count').sort_values('user_id', ascending = False)[-3:])

