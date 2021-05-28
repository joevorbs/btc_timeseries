import pandas as pd 
import numpy as np
import statistics
import scipy.stats as st
from fbprophet import Prophet
from fbprophet.diagnostics import performance_metrics
import pystan
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import date
import time

#Current date
today = datetime.now().date()

#Minimum and maxium lead times (in days)
min_leads, max_leads = [183,730] #About half a year to 2 years

#Cutoff for lead times in days - if every lead is included we will have a one row dataset
cutoff = range(min_leads, max_leads)

#Target for variable selection
target = "Closing Price (USD)"

#Path to save to
path = "/Users/joevorbeck/Documents/btc_timeseries/multivariate_feature_list/"

#Read in analytical dataset comprised of blockchain and bitcoin data
btc = pd.read_csv("btc_analytical_dataset" + str(today) + ".csv")

#Remove unnecessary column
btc.drop(["Currency","Unnamed: 0"], axis = 1, inplace = True)

#Convert Timestamp to datetime - need for interpolation
btc['Timestamp'] = pd.to_datetime(btc['Timestamp'], yearfirst = True)

#Interpolate missing values - we have BTC price data for everyday but not every blockchain metric is tracked everyday
#Can use a timeseries based method to interpolate missing values - imputing averages won't work in BTC case
btc_interp = btc.set_index("Timestamp").interpolate("time", axis = 0)

#Drop rows were interpolation cant fill rows & reset index so timestamp is used as a column
btc_interp = btc_interp.dropna().reset_index()

#Rename timestamp for prophet
btc_interp.rename(columns = {'Timestamp' : 'ds'}, inplace = True)

#Empty dataframe to store residuals 
btc_residuals = pd.DataFrame()

#List of columns to iterate through - ignoring our target variable and date
col_list = new_df.columns.remove[target, "ds"]]

#Loop for all variables minus the target and obtain their residuals
for i in col_list:
    ts = Prophet(daily_seasonality = False)
    cols_to_use = btc_interp[["ds", i]].rename(columns = {i : "y"})
    ts.fit(cols_to_use)
    preds = ts.predict(cols_to_use)
    btc_residuals[i] = cols_to_use['y'] - preds['yhat']

#Initialize empty df to store leads
new_df = pd.DataFrame()

#Cutoff for lead times in days - if every lead is included we will have a one row dataset
cutoff = range(0, lags) #2 Years 

#Need to reverse dataset order to place most recent observations at the top
btc_residuals_flip = btc_residuals.iloc[::-1]

#For every column, create a new column based off every single possible lead time in the specified range and append to a blank df
for i in btc_residuals_flip.columns:
    for j in cutoff:
        new_col = btc_residuals_flip[i].shift(j)
        new_df[str(i) + "_" + str(j)] = new_col  #Name of each column is the column name with the lead time as a suffix

#Trim off rows with subsequent missing values
new_df.dropna(inplace = True)

#Flip dataset back to original order
new_df = new_df.iloc[::-1]

#Reset index to append target back to dataset - will try to match up rows based on the index
new_df = new_df.reset_index().drop("index", axis = 1)

#Append target back to dataframe  of led features - will be (N - L; number of rows - leads)
new_df["Target"] = btc_interp[target][0:len(new_df)]

#Isolate features & target
X = final_df.drop(target, axis = 1)
y = final_df[target]

#Train/test split - want to keep 2/3 of the data for training, 1/3 for testing
X_train = X[0:round(len(X) * .66)]
X_test = X[len(X_train):]

y_train = y[0:round(len(y) * .66)]
y_test = y[len(y_train):]

#Initialize lasso regression - regularization will help eliminate any non-signifcant lead times - can use CV if data is prewhitened
lasso_cv = LassoCV(cv = 5, n_alphas = 100, max_iter = 1000, normalize = True) 

#Fit model to training data
lasso_cv.fit(X_train, y_train)
#Predict on test set and assess model
lasso_cv.predict(X_test)

#Get coefficients from model paired with names
coefs = pd.DataFrame(list(zip(lasso_cv.coef_, X_train.columns))).rename(columns = {0 : "Beta", 1 : "Feature"})
#Filter any coefficients shrunk to 0
coefs_final_list = coefs[coefs['Beta'] > 0]
#Write out list of features for the forecasting model
coefs_final_list['Feature'].to_csv(path + "feature_list_" + str(today) + ".csv")
