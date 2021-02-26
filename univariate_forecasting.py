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

#Read in BTC historical price data - obtained from Coindesk
btc = pd.read_csv("btc_20210225.csv")

#Remove unnecessary column
btc.drop("Currency", axis = 1, inplace = True)

#Convert date column to proper format and rename for prophet - need to rename target as well
btc['Date'] = pd.to_datetime(btc['Date'], yearfirst = True, errors = 'coerce')
btc.rename(columns = {'Date' : 'ds', 'Closing Price (USD)' : 'y'}, inplace = True)

#List to use for transformations and missing values - include everything except the datestamp
list_to_use = [x for x in btc.columns if x not in "ds"]

#Incase of any nan or inf values, replace with 0 for now and ignore - other imputation / transformation strategies can be used here
btc = btc.replace([np.nan, -np.inf, np.inf], 0)

#Drop any columns which contain 0s - will need to be adjusted probably when more data is added
for i in btc.columns:
    if 0 in list(btc[i].values):
        btc.drop(i, inplace = True)

#Log transform variables using list that excludes ds - log10 smooths better
#for i in list_to_use:
    #btc[i] = np.log10(btc[i])

#Standardize variables
#std = StandardScaler()    #Keeping variables untransformed for sake of pure forecast currently - converting a log transformed variable back to its natural scale can inflate model errors

#btc_log_std = pd.DataFrame(std.fit(btc.drop("ds", axis = 1)).transform(btc.drop("ds", axis = 1)))
#btc_log_std.columns = btc.columns[1:]
#btc_log_std['ds'] = btc['ds']

#Use prophet to create univariate forecasts for each model

#Easy switch to change number of years for future predictions
year_mult = 2

#Loop for every variable and develop a univariate forecast 
for i in btc.columns[1:]:
    ts = Prophet(daily_seasonality = False,    #testing many different parameters, why not!
                 growth = 'logistic',
                changepoint_prior_scale=0.25)  #Increasing changepoint increases forecast uncertainty - better in btc case and strong bull market - default is .05
    ts.add_country_holidays(country_name='US')

    
    cols_to_use = btc[["ds", i]].rename(columns = {i : "y"})  
    cols_to_use['cap'] = 100000 #Setting a cap on prediction for logistic growth
    
    ts.fit(cols_to_use)
    
    future_days = ts.make_future_dataframe(periods=365 * year_mult) #Change number of years with year_mult, 1 increase is 1 increase in year
    future_days['cap'] = 100000 #Setting cap for future df
    
    preds = ts.predict(future_days)
    
    ts.plot(preds)
    plt.title(i)

