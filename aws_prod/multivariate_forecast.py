import pandas as pd 
import numpy as np
from sklearn.linear_model import LassoCV, Ridge
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
import time
import boto3
import s3fs

#Current date
today = datetime.now().date()

#Minimum and maxium lead times (in days)
min_leads, max_leads = [183,730] #About half a year to 2 years

#Cutoff for lead times in days - if every lead is included we will have a one row dataset
cutoff = range(min_leads, max_leads)

#Target for forecast
target = "Closing Price (USD)"

#Path to obtain model features
path = "/home/ec2-user/repos/btc_timeseries/aws_prod/multivariate_feature_list/"

#Read in analytical dataset comprised of blockchain and bitcoin data
btc = pd.read_csv("s3://analytical-datasets/btc_analytical_dataset" + str(today) + "csv")

#Read in list of features
features_list = pd.read_csv(path + "feature_list_" + str(today) + ".csv")

#Only include features chosen by the prior lasso
###need to make the trimming programmatic
features_list_trimmed = set([i[:-4] for i in features_list['Feature'].values]) #Trim off lead time suffix to use a filter on normal col names
btc_filtered = btc[[*features_list_trimmed]]

#Convert Timestamp to datetime - need for interpolation
btc_filtered['Timestamp'] = pd.to_datetime(btc['Timestamp'], yearfirst = True)

#Interpolate missing values - we have BTC price data for everyday but not every blockchain metric is tracked everyday
#Can use a timeseries based method to interpolate missing values - imputing averages won't work in BTC case
btc_interp = btc_filtered.set_index("Timestamp").interpolate("time", axis = 0)

#Drop rows were interpolation cant fill rows & reset index so timestamp is used as a column
btc_interp = btc_interp.dropna().reset_index()

#Reverse the order of the dataset to create leads
btc_filtered_reverse = btc_interp.iloc[::-1]
#Drop timestamp
btc_filtered_reverse.drop("Timestamp", axis =  1, inplace = True)

#Create empty df to store led dataframe
btc_ml_df = pd.DataFrame()

#For every column, create a new column based off every single possible lead time in the specified range and append to a blank df
for i in btc_filtered_reverse.columns:
    for j in cutoff:
        new_col = btc_filtered_reverse[i].shift(j)
        btc_ml_df[str(i) + "_" + str(j)] = new_col  #Name of each column is the column name with the lead time as a suffix

#Drop blank rows
btc_ml_df.dropna(inplace = True)

#Re-reverse order to keep natural order of the data - important for the model
btc_ml_df = btc_ml_df.iloc[::-1]

#Filter out any variables that weren't chosen by the previous lasso
btc_ml_df_final = btc_ml_df.filter(features_list["Feature"].values)

#Append target back to dataframe of chosen led features
btc_ml_df_final[target] = btc[target][0:len(btc_ml_df_final)]

#Isolate features & target
X = btc_ml_df_final.drop(target, axis = 1)
y = btc_ml_df_final[target]

#Train/test split - same split but mostly used for training and insight to performance
X_train = X[0:round(len(X) * .66)]
X_test = X[len(X_train):]

y_train = y[0:round(len(y) * .66)]
y_test = y[len(y_train):]

#Initialize ridge / LS model
ridge = Ridge()
#Fit ridge to training set
ridge.fit(X_train, y_train)
#Predict on test set and check performance
ridge.predict(X_test)

#Create a new dataset to be used explicity for the forecast
X_forecast_df = X.iloc[len(X) - min_leads: len(X)] # Can only forecast as far out as the number of minimum leads used

#Initialize new ridge
ridge_forecast = Ridge()
#Fit ridge to entire un-transformed dataset 
ridge_forecast.fit(X, y)
#Predict target and generate forecast
ridge.predict(X_forecast_df)

#Generate plot of actual, predicted, and forecasted values