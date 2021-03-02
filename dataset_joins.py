import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import time
import glob

#Current date
today = datetime.now().date()

#Read in BTC historical price data - obtained from Coindesk
btc = pd.read_csv("btc_20210228.csv")
#Rename column & convert type to be consistent with blockchain dataq
btc.rename(columns = {"Date" : "Timestamp"}, inplace = True)
btc['Timestamp'] = pd.to_datetime(btc['Timestamp'], yearfirst = True, errors = 'coerce')

#Read in scraped blockchain data from blockchain.com
repo_files = glob.glob("/Users/joevorbeck/Documents/btc_timeseries/blockchain_data/*.csv")

#Read in all dfs and append to a list
blockchain_dfs = []

for filename in repo_files:
    df = pd.read_csv(filename)
    blockchain_dfs.append(df)

#Start with a copy of btc and join each subsequent metric dataframe
merged_df = btc

#Start with BTC price dataframe on the left as we have data for every single day - different metrics are missing days or weren't tracked at certain times
for df in li:
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], yearfirst = True, errors = 'coerce')
    merged_df = test.merge(df, on = "Timestamp", how = "left")

#Write out analytical dataset to repo
merged_df.to_csv("/Users/joevorbeck/Documents/btc_timeseries/analytical_datasets/btc_analytical_dataset" + str(today) + ".csv")

