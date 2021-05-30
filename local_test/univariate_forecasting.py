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

#Current date
today = datetime.now().date()

#Read in BTC historical price data - obtained from Coindesk
btc = pd.read_csv("btc_" + str(today)+ ".csv")

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

#Use prophet to create univariate forecasts for each model

#Easy switch to change number of years for future predictions
year_mult = 2


#Create df for 'holidays' - specific dates to model, using btc halving dates
holidays = pd.DataFrame({
  'holiday': 'halving',
  'ds': pd.to_datetime(['2012-10-28', '2016-07-09', '2020-05-11']),
  'lower_window': 0,
  'upper_window': 1,
})

#Loop for every variable and develop a univariate forecast - will implement grid search soon
for i in btc.columns[1:]:
    ts = Prophet(daily_seasonality = False,    #testing different parameters, why not!
                 growth = 'logistic',
                changepoint_prior_scale=0.25, #Increasing changepoint increases forecast uncertainty - better in btc case - default is .05
                interval_width=0.9, #Can change uncertainty intervals - assistive when modeling more rate changes
                holidays = holidays) 
    
    ts.add_country_holidays(country_name='US')

    
    cols_to_use = btc[["ds", i]].rename(columns = {i : "y"})  
    cols_to_use['cap'] = 100000 #Setting a cap on prediction for logistic growth
    
    ts.fit(cols_to_use)
    
    future_days = ts.make_future_dataframe(periods = 365 * year_mult) #Change number of years with year_mult, 1 increase is 1 increase in year
    future_days['cap'] = 100000 #Setting cap for future df
    
    preds = ts.predict(future_days)
    
    #Regression metrics for plotting
    mae = 1/len(btc) * abs(btc['y'] - preds['yhat']).sum()
    rmse = np.sqrt((((btc['y'] - preds['yhat']).sum())**2)) / len(btc['y'])
    r2 = 1 - ((btc['y'] - preds['yhat'])**2).sum() / ((btc['y'] - btc['y'].mean())**2).sum()
    
    ts.plot(preds)
    
    #Including halving dates and model metrics on charts
    plt.axvline(x=dt.datetime(2016,7,9), color='b', label='axvline - full height')
    plt.axvline(x=dt.datetime(2020,5,11), color='b', label='axvline - full height')
    plt.title(i + "\n R2: " + str(r2) + "\n MAE: " + str(mae) + "\n RMSE: " + str(rmse))
