import pandas as pd 
import numpy as np
from sklearn.linear_model import LassoCV, Ridge
from sklearn.metrics import mean_absolute_error as MAE
from sklearn.metrics import mean_squared_error as MSE
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
import time
import boto3
import s3fs

#Current date
today = datetime.now().date()

#Minimum and maxium lead times (in days)
min_leads, max_leads = [1,183] #Up to a half a year

#Cutoff for lead times in days - if every lead is included we will have a one row dataset
cutoff = range(min_leads, max_leads + 1) #Range is not inclusive

#Target for forecast
target = "Closing Price (USD)"

#Path to obtain model features
#path = "/home/ec2-user/repos/btc_timeseries/aws_prod/multivariate_feature_list/"

#Read in analytical dataset comprised of blockchain and bitcoin data
btc = pd.read_csv("s3://analytical-datasets/btc_analytical_dataset"+ str(today) + ".csv")

#Read in list of features
features_list = pd.read_csv("s3://multivariate-features/" + "feature_list_" + str(today) + ".csv")

#Only include features chosen by the prior lasso
###need to make the trimming programmatic
features_list_trimmed = set([i.split("_")[0] for i in features_list['Feature'].values]) #Trim off lead time suffix to use a filter on normal col names
btc_filtered = btc[[*features_list_trimmed]]
#Need to append timestamp for interpolation
btc_filtered['Timestamp'] = btc['Timestamp'] 
#Convert Timestamp to datetime
btc_filtered['Timestamp'] = pd.to_datetime(btc['Timestamp'], yearfirst = True)

#Interpolate missing values - we have BTC price data for everyday but not every blockchain metric is tracked everyday
#Can use a timeseries based method to interpolate missing values - imputing averages won't work in BTC case
btc_interp = btc_filtered.set_index("Timestamp").interpolate("time", axis = 0)

#Fill rest of missing values with the avereage
btc_interp.fillna(btc_interp.mean(), inplace = True)

#Aggregate by day to deal with duplication - some of the metrics are reported more than once a day - ones that are once a day won't be affected by this
btc_interp = btc_interp.groupby("Timestamp").agg("mean")

#Drop rows were interpolation cant fill rows & reset index so timestamp is used as a column
btc_interp = btc_interp.dropna().reset_index()

#Reverse the order of the dataset to create leads
btc_filtered_reverse = btc_interp.iloc[::-1]

#Drop timestamp
btc_filtered_reverse.drop("Timestamp", axis =  1, inplace = True)

#Need to process the target the samae way to append to the df
btc_target = btc[['Timestamp', target]]
btc_target = btc_target.groupby("Timestamp").agg("mean")[::-1].reset_index() #Reverse and reset index to be able to append to the reversed df made below

#Create empty df to store offset dataframe
btc_ml_df = pd.DataFrame()

#For every column, create a new column based off every single possible lead time in the specified range and append to a blank df
for i in btc_filtered_reverse.columns:
    for j in cutoff:
        x = -abs(j) #Need to create offsets from the bottom
        new_col = btc_filtered_reverse[i].shift(x)
        btc_ml_df[str(i) + "_" + str(j)] = new_col  #Name of each column is the column name with the lead time as a suffix

#Reset so target matches indices
btc_ml_df = btc_ml_df.reset_index()

#Append target back to dataframe of chosen led features
btc_ml_df[target] = btc_target[target]

#Drop blank rows
btc_ml_df.dropna(inplace = True)

#Re-reverse order to keep natural order of the data - important for the model
btc_ml_df = btc_ml_df.iloc[::-1]

#Filter out any variables that weren't chosen by the previous lasso
btc_ml_df_final = btc_ml_df[[*features_list["Feature"].values, target]]

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
mae = MAE(ridge.predict(X_test), y_test) #MAE
mse = MSE(ridge.predict(X_test), y_test, squared = True) #MSE
rmse = MSE(ridge.predict(X_test), y_test, squared = False) #RMSE
#Save daily model metrics to s3
metrics = pd.DataFrame([mae,mse,rmse]).T.rename(columns = {0:"MAE", 1:"MSE", 2:"RMSE"})
metrics.to_csv("s3://forecast-metrics/model_metrics_" + str(today) + ".csv")
          
#Create a new dataset to be used explicityfor the forecast
X_forecast_df = X.iloc[len(X) - min_leads: len(X)] # Can only forecast as far out as the number of minimum leads used

#Initialize new ridge
ridge_forecast = Ridge() 
#Fit ridge to entire un-transformed dataset 
ridge_forecast.fit(X, y)
#Predict target and generate forecast
ridge_forecast.predict(X_forecast_df)
#Save daily prediction
forecasted_value = pd.DataFrame(ridge_forecast.predict(X_forecast_df), columns = ["BTC Closing Price"])
forecasted_value.to_csv("s3://forecast-vis/btc_pred_" + str(today) + ".csv")

#Generate plot of actual, predicted, and forecasted values
