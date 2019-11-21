# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 09:57:09 2019

@author: Nick
"""

#import json
import pandas as pd
pd.options.display.max_columns = 500

#Read it in as a raw json
#with open('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\4\\song.json', 'r') as file:
#    data = json.load(file)
    
#This is gross.  Let's try pandas
data = pd.read_json('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\4\\song.json')
#Much better

#Top 3 states by number of users
#This does unique users
print('Unique Users')
print('Top three states: ')
print(data[['user_id', 'user_state']].groupby('user_state').agg({'user_id':pd.Series.nunique}).sort_values('user_id', ascending = False)[1:4])
print('Bottom three states: ')
print(data[['user_id', 'user_state']].groupby('user_state').agg({'user_id':pd.Series.nunique}).sort_values('user_id', ascending = False)[-3:])

#We should really look at total number of songs played per state, not unique users
print('\nEngagement (songs played)')
print('Top three states: ')
print(data[['user_id', 'user_state']].groupby('user_state').agg('count').sort_values('user_id', ascending = False)[1:4])
print('Bottom three states: ')
print(data[['user_id', 'user_state']].groupby('user_state').agg('count').sort_values('user_id', ascending = False)[-3:])

#Let's briefly look at number of songs played per user
data['user_id'].value_counts().hist()
#Doesn't seem too unexpected.  Let's move on

#Return a list of the first users who signed up in each state
print('\nFirst user in each state')
print(data.sort_values('user_sign_up_date').drop_duplicates(subset = 'user_state'))

#Function that returns the most likely song to be played after a song

def NextSong(currSong):
    #First get all the data that goes with this song
#    df = data.loc[data['song_played'] == currSong, :]
    
    #This is the most  memory expensive way to do this
    df = data.sort_values(by = ['user_id', 'time_played'])
    df.reset_index(inplace = True)
    #Get the index of all the song
    indices = df.loc[df['song_played'] == currSong, :].index
    #Then look at index + 1 (since we've sorted on time_played)
    #ensuring the user_id is the same as that in index
    temp = {} #Dictionary will be a histogram of songs played
    for i in indices:
        if df.loc[i + 1, 'user_id'] == df.loc[i, 'user_id']:
            song = df.loc[i + 1, 'song_played']
            if song in temp.keys():
                temp[song] += 1
            else:
                temp[song] = 1
    #This is a dictionary (histogram) that could be maintained in real time
    
    #if empty dictionary just pick any song randomly from the overall distribution
    if not temp:
        return(df['song_played'].sample(n = 1).values[0]) #This is inefficient
        #Better way would be to keep a histogram of songs and update it real time
        #Then just sample from that
    else:
        return(list(temp.keys())[list(temp.values()).index(max(list(temp.values())))])
    
#test it out
print('Testing most likely next song')
print('Current song = Hey Judge')
print('Next song = ' + NextSong('Hey Jude'))
#Things to consider that I'm not doing:
#1. Should not consider next song if time different between next and current is too large
#2. Returning the same song can lead to an infinite loop if this is actually used for recommendations
#3. My implementation does not address the question, which is user specific
# Being user specific would lead to a whole lot of cases of a pointless result, as the user
# may have only listened to it once.  Dumb idea imo.  Mine is generalized and could easily
# be tailed to narrow in on only the specific user (one additional line to scrub df)

#Setting up a test to see if this works well would be to see if the number of song skips
#has increased after implementing this method