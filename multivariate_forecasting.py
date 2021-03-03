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

#Read in analytical dataset comprised of blockchain and bitcoin data
btc = pd.read_csv("btc_analytical_dataset" + str(today) + ".csv")

#Remove unnecessary column
btc.drop(["Currency","Unnamed: 0"], axis = 1, inplace = True)

#Convert Timestamp to datetime - need for interpolation
btc['Timestamp'] = pd.to_datetime(btc['Timestamp'], yearfirst = True)

#Interpolate missing values - we have BTC price data for everyday but not every blockchain metric is tracked everyday
#Can use a timeseries based method to interpolate missing values - imputing averages won't work in BTC case
btc_interp = btc.set_index("Timestamp").interpolate("time", axis = 0)

#Initialize empty df
new_df = pd.DataFrame()

#Cutoff for lead times in days - if every lead is included we will have a one row dataset
cutoff = range(0, 1000)

#For every column, create a new column based off every single possible lead time and append to a blank df
for i in btc_interp.columns:
    for j in cutoff:
        new_col = btc_interp[i].shift(j)
        new_df[str(i) + "_" + str(j)] = new_col  #Name of each column is the column name with the lead time as a suffix

#Trim off rows with subsequent missing values
new_df.dropna(inplace = True)