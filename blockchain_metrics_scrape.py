import warnings
warnings.simplefilter(action='ignore')

import pandas as pd
import numpy as np
from selenium import webdriver
from datetime import datetime
from datetime import date
import time
import shutil

#Current date
today = datetime.now().date()

#Path to downloads folder
dl_path = "/Users/joevorbeck/Downloads/"

#Using webdriver automation to scrape different daily blockchain metrics
driver = webdriver.Chrome("/Users/joevorbeck/desktop/chromedriver")

#List of pages from blockchain.com to obtain data from
pages = ["https://www.blockchain.com/charts/total-bitcoins",
         "https://www.blockchain.com/charts/blocks-size",
         "https://www.blockchain.com/charts/hash-rate",
         "https://www.blockchain.com/charts/n-unique-addresses",
         "https://www.blockchain.com/charts/my-wallet-n-users"]

#List of related metrics to scrape for website section
currency_statistics = ["Total Circulating Bitcoin",
                      "Market Price",
                      "Market Capitalization (USD)",
                      "Exchange Trade Volume (USD)"]

block_details = ["Blockchain Size (MB)",
                 "Total Number of Transactions"]


mining_info = ["Network Difficulty",
              "Miners Revenue (USD)",
              "Total Transaction Fees (BTC)",
              "Cost Per Transaction"]

network_activity = ["Unspent Transaction Outputs",
            "Unique Addresses Used",
            "Confirmed Transactions Per Day",
            "Confirmed Payments Per Day",
            "Output Value Per Day",
            "Estimated Transaction Value (BTC)",
            "Transactions Excluding Popular Addresses"]

wallet_activity = ["Blockchain.com Wallets"]

#all_metrics_to_scrape = [currency_statistics, block_details, network_activity, mining_info, wallet_activity]

#Currency Statistics
driver = webdriver.Chrome("/Users/joevorbeck/desktop/chromedriver")
driver.get(pages[0])

for i in currency_statistics:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "/*.csv"):
        print("Moving " + j + " to git repo")
        shutil.move(j, "/Users/joevorbeck/Documents/btc_timeseries/blockchain_data/" + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Block Details
driver = webdriver.Chrome("/Users/joevorbeck/desktop/chromedriver")
driver.get(pages[1])

for i in block_details:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "/*.csv"):
        print("Moving " + j + " to git repo")
        shutil.move(j, "/Users/joevorbeck/Documents/btc_timeseries/blockchain_data/" + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Mining Info
driver = webdriver.Chrome("/Users/joevorbeck/desktop/chromedriver")
driver.get(pages[2])

for i in mining_info:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "/*.csv"):
        print("Moving " + j + " to git repo")
        shutil.move(j, "/Users/joevorbeck/Documents/btc_timeseries/blockchain_data/" + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Network Activity
driver = webdriver.Chrome("/Users/joevorbeck/desktop/chromedriver")
driver.get(pages[3])

for i in network_activity:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "/*.csv"):
        print("Moving " + j + " to git repo")
        shutil.move(j, "/Users/joevorbeck/Documents/btc_timeseries/blockchain_data/" + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Wallet Activity
driver = webdriver.Chrome("/Users/joevorbeck/desktop/chromedriver")
driver.get(pages[4])

for i in wallet_activity:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "/*.csv"):
        print("Moving " + j + " to git repo")
        shutil.move(j, "/Users/joevorbeck/Documents/btc_timeseries/blockchain_data/" + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")
