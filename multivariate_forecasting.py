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

cd Desktop

#Read in BTC historical price data - obtained from Coindesk
btc = pd.read_csv("btc_20210225.csv")

#Remove unnecessary column
btc.drop("Currency", axis = 1, inplace = True)


test = pd.DataFrame(btc['Closing Price (USD)']).reset_index()

#Create key-value pair to swap index of lead/lag times with correct index (ex: 0 to 100 -> -50 to 50)

#Max number of lags
maxlags = len(btc) - 1 

#Correlate any 2, just need index [0]
lead_and_lags = plt.xcorr(btc['Closing Price (USD)'], btc['24h Low (USD)'], maxlags = maxlags)[0] 
#Index we want to change
lead_lags_to_change = list(btc.index)

#Create dictionary to map new values to old index
val_map = dict(zip(lead_lags_to_change, lead_and_lags))
lead_lags_updated = list(pd.Series(test['index']).replace(val_map))

#Append new index to df
test['index'] = lead_lags_updated

#Initialize empty df
new_df = pd.DataFrame()

#For every column, create a new column based off every single possible lead time and append to a blank df
for i in lead_lags_updated:
    new_col = test['Closing Price (USD)'].shift(i)
    new_df['cp_' + str(i)] = new_col #CP is coin price, temporary, will use real names


#new_df.drop(pd.isnull())


