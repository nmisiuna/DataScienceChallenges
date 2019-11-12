# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 09:54:48 2019

@author: Nick
"""

import pandas as pd
pd.options.display.max_columns = 500

emails = pd.read_csv('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\3\\email_table.csv')
opened = pd.read_csv('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\3\\email_opened_table.csv')
clicked = pd.read_csv('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\3\\link_clicked_table.csv')

#I want to create a column in my emails dataframe for opened and clicked
emails['opened'] = False
emails.loc[emails['email_id'].isin(opened['email_id']), 'opened'] = True
emails['clicked'] = False
emails.loc[emails['email_id'].isin(clicked['email_id']), 'clicked'] = True