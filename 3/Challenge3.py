# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 09:54:48 2019

@author: Nick
"""

import pandas as pd
pd.options.display.max_columns = 500
import prince
import sklearn.linear_model as lm
from sklearn.preprocessing import OneHotEncoder as OHE, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import GradientBoostingClassifier as GBC

emails = pd.read_csv('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\3\\email_table.csv')
opened = pd.read_csv('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\3\\email_opened_table.csv')
clicked = pd.read_csv('C:\\Users\\Nick\\Documents\\GitHub\\DataScienceChallenges\\3\\link_clicked_table.csv')

#I want to create a column in my emails dataframe for opened and clicked
emails['opened'] = False
emails.loc[emails['email_id'].isin(opened['email_id']), 'opened'] = True
emails['clicked'] = False
emails.loc[emails['email_id'].isin(clicked['email_id']), 'clicked'] = True
emails.set_index('email_id', inplace = True)

#Percent of users who opened the email
print('Percent opened: {f:2.2f}%'.format(f = emails['opened'].sum() / emails.shape[0] * 100.0))

print('Percent clicked (who opened): {f:2.2f}%'.format(f = 
        emails['clicked'].sum() / emails['opened'].sum() * 100.0))

#Let's try MCA
mca = prince.MCA(n_components = 2)
mca = mca.fit(emails.astype('object'))
ax = mca.plot_coordinates(X=emails.astype('object'),
                          ax=None, figsize=(10, 10), show_row_points=False,
                          row_points_size=10, show_row_labels=False,
                          show_column_points=True, column_points_size=30,
                          show_column_labels=True, legend_n_cols=1)
ax.get_figure()

#logistic regression
temp = emails[['email_text', 'email_version', 'hour', 'weekday', 'user_country']]
temp = pd.get_dummies(temp)
X = temp.join(emails[['user_past_purchases']])
y = emails['clicked']

#I'd like to do this with cross validation
model = lm.LogisticRegression()
scores = cross_val_score(model, X, y, cv = 10)
#Works pretty good!
#What about confusion matrix
y_pred = cross_val_predict(model, X, y, cv = 10)
conf = confusion_matrix(y, y_pred)
for i in range(len(conf)):
    conf[i] = conf[i] / sum(conf[i])
#This is alarming.  The model is overfit and merely predicts everything as 
#It also sucks to interpret without labels.  Let's use pandas:
conf = pd.crosstab(y, y_pred, rownames = ['True'], colnames = ['Predicted'], margins = True)
print(conf)

#We need to handle unbalanced classes
model = lm.LogisticRegression(class_weight = 'balanced')
scores = cross_val_score(model, X, y, cv = 10)
y_pred = cross_val_predict(model, X, y, cv = 10)
conf = pd.crosstab(y, y_pred, rownames = ['True'], colnames = ['Predicted'], margins = True)
print(conf)

#Try gradient boosting
XTrain, XTest, yTrain, yTest = train_test_split(X, y)
scaler = MinMaxScaler()
XTrain = scaler.fit_transform(XTrain)
X = scaler.fit_transform(X)
model = GBC(n_estimators = 100, min_samples_split = 0.01, min_samples_leaf = 50)
model.fit(XTrain, yTrain)
model.score(XTest, yTest)
#y_pred = model.predict(XTest)
y_pred = cross_val_predict(model, X, y, cv = 10)
conf = pd.crosstab(y, y_pred, rownames = ['True'], colnames = ['Predicted'], margins = True)
print(conf)
#This all isn't really the point, however
#The challenge wants to know how to send emails to maximize click-rate
#Therefore, we really want to understand how the features work together


#Let's investigate our model somewhat to see what the coefficients are
temp = emails[['email_text', 'email_version', 'hour', 'weekday', 'user_country']]
temp = pd.get_dummies(temp)
X = temp.join(emails[['user_past_purchases']])
scaler = MinMaxScaler()
XNorm = scaler.fit_transform(X)  #If we don't scale we can't really interpret coefficients
y = emails['clicked']

model = lm.LogisticRegression(class_weight = 'balanced')
out = model.fit(XNorm, y)
temp = pd.DataFrame(columns = ['Feature', 'Coefficient'])
temp['Feature'] = X.columns
temp['Coefficient'] = out.coef_[0]
print(temp.sort_values('Coefficient', ascending = False))
#This tells us a lot more
#These coefficients now have a lot of meaning
#user_past_purchases is the most important feature by far
#UK and US users are much more likely to click than ES and FR
#Wed/Thur/Tue/Mon are good days to send emails on.  The rest are not
#A personalized email is better than generic, and short is better than long

#Let's do some more investigating 
pd.pivot_table(emails, values = 'clicked', columns = 'user_past_purchases', aggfunc = sum)
temp = emails.loc[emails['user_past_purchases'] < 17]
pd.pivot_table(temp, values = 'clicked', columns = 'user_past_purchases', aggfunc = 'count') 




