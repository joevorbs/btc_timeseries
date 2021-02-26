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

#Convert date column to proper format and rename for prophet - need to rename target as well
btc['Date'] = pd.to_datetime(btc['Date'], yearfirst = True, errors = 'coerce')
btc.rename(columns = {'Date' : 'ds', 'Closing Price (USD)' : 'y'}, inplace = True)

#Remove unnecessary column
btc.drop("Currency", axis = 1, inplace = True)

#Drop missing values
list_to_use = [x for x in btc.columns if x not in "ds"]

btc = btc.replace([np.nan, -np.inf, np.inf], 0)

for i in btc.columns:
    if 0 in list(btc[i].values):
        btc.drop(i, inplace = True)

#Log transform variables
for i in list_to_use:
    btc[i] = np.log(btc[i])

#Run prophet on all variables to obtain their residuals

#Empty dataframe to store residuals
btc_residuals = pd.DataFrame()

#Loop for all variables
for i in list_to_use:
    ts = Prophet()
    cols_to_use = btc[["ds", i]].rename(columns = {i : "y"})
    ts.fit(cols_to_use)
    preds = ts.predict(cols_to_use)
    btc_residuals[i] = cols_to_use['y'] - preds['yhat']

#Need to reverse the order of the dataset - xcorr function denotes leads with positive integers..need to swap this
reverse_btc_residuals = btc_residuals.iloc[::-1]
 
#Run a cross correlation on all the residuals
btc_cross_corr = pd.DataFrame()
maxlags = len(btc) - 1

for i in reverse_btc_residuals.columns:
    cross_corr = pd.Series(plt.xcorr(reverse_btc_residuals[i], reverse_btc_residuals['y'], maxlags = maxlags)[1])
    btc_cross_corr[i] = cross_corr

#Find statistically significant lead/lag times for each set of correlation coefficients
p_values = []
r_values = []
variables = []
lead_lags = []

n = len(btc)

for i in btc_cross_corr.columns:
    r = pd.Series(btc_cross_corr[i])
    test_stat = r*np.sqrt((n-2)/(1-r*r))
    p_val = pd.Series(st.norm.sf(np.abs(test_stat))*2)
    
    p_and_r_vals = pd.concat([r, p_val], axis = 1).reset_index()
    p_and_r_vals.rename(columns = {0 : "p"}, inplace = True)
    
    signif_p_vals = p_and_r_vals[p_and_r_vals["p"] < .05]
    most_signif = signif_p_vals[signif_p_vals["p"] == signif_p_vals["p"].min()]
        
    p_values.append(most_signif["p"].values[0])
    r_values.append(most_signif[i].values[0])
    variables.append(i)
    lead_lags.append(most_signif['index'].values[0])

#Create key-value pair to swap index of lead/lag times with correct index (ex: 0 to 100 -> -50 to 50)
lead_and_lags = plt.xcorr(reverse_btc_residuals['24h High (USD)'], reverse_btc_residuals['y'], maxlags = maxlags)[0]
#Index we want to change
lead_lags_to_change = list(btc_cross_corr.index)

#Create dictionary to map new values to old index
val_map = dict(zip(lead_lags_to_change, lead_and_lags))
lead_lags_updated = list(pd.Series(lead_and_lags).replace(val_map))

#Fill out empty dataframe
indicators = pd.DataFrame()

indicators['variable'] = variables
indicators['r'] = r_values
indicators['p'] = p_values
indicators['lags'] = lead_lags_updated

#Ignore variables who are most correlated with the target with no lead/lags
indicators = indicators[indicators['lags'] != 0]

#Split indicators df into positively leading & lagging, and negtiavely leading & lagging dfs
indicators_p_lead = indicators[(indicators.r > 0 and indicators.lags < 0)]
indicators_p_lag = indicators[(indicators.r > 0 and indicators.lags > 0)]
                               
indicators_n_lead = indicators[(indicators.r < 0 and indicators.lags < 0)]
indicators_n_lag = indicators[(indicators.r < 0 and indicators.lags > 0)]

