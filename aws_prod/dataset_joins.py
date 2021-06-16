import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
import time
import glob
import boto3
import s3fs

#Current date
today = datetime.now().date()

#Path to s3 bucket from webscrape
s3_path = "s3://blockchain-scrape/"

#Initialize resource to s3 and connect to the webscrape bucket
s3 = boto3.resource('s3')
my_bucket = s3.Bucket('blockchain-scrape')

#Read in BTC historical price data - obtained from Coindesk
btc = pd.read_csv("s3://btc-coindesk/btc_" + str(today) + ".csv")

#Rename column & convert type to be consistent with blockchain data
btc.rename(columns = {"Date" : "Timestamp"}, inplace = True)
btc['Timestamp'] = pd.to_datetime(btc['Timestamp'], yearfirst = True)

#Read in all dfs from s3 and append to a list
blockchain_dfs = []
for file in my_bucket.objects.all():
    blockchain_dfs.append(file.key)

#Filter files for today's run
blockchain_dfs = [x for x in blockchain_dfs if str(today) in x]

#Create list to append dfs read in from s3
df_list = []
for filename in blockchain_dfs:
    df = pd.read_csv(s3_path + filename)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'].map(lambda x: str(x)[0:10]), format='%Y/%m/%d')   #For every blockchain df, trim off the minutes and seconds, etc. in the Timestamp column and convert to datetime
    df_list.append(df)

#Start with a copy of btc and join each subsequent metric dataframe
merged_df = btc

#Start with BTC price dataframe on the left as we have data for every single day - different metrics are missing days or weren't tracked at certain times
for df in df_list:
    merged_df = merged_df.merge(df, on = "Timestamp", how = "left")

#Clean up artifacts from the join
merged_df = merged_df.T.drop_duplicates().T.drop(['Unnamed: 0_x', 'Unnamed: 0_y'], axis = 1)

#Write out analytical dataset to s3
merged_df.to_csv("s3://analytical-datasets/btc_analytical_dataset" + str(today) + ".csv")
