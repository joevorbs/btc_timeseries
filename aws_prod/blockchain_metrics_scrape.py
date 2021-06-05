import warnings
warnings.simplefilter(action='ignore')

import pandas as pd
import numpy as np
import boto3
import s3fs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from datetime import datetime
from datetime import date
import time
import shutil
import glob

#Current date
today = datetime.now().date()

#Path to download folder
dl_path = "/home/ec2-user/scraped_files/"

#Path to repo folder
repo_path = "/home/ec2-user/repos/btc_timeseries/aws_prod/blockchain_data/"

#Path to chromedriver
driver_path = "/usr/bin/chromedriver"

#Options to run headless chrome on linux
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("no-sandbox")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--headless")
chrome_options.add_argument("—disasble-dev-shm-usage")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('start-maximized') 
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--window-size=1280x1696')

chrome_options.add_experimental_option("prefs", {
  "download.default_directory": dl_path,
  "download.prompt_for_download": False,
})

#List of pages from blockchain.com to obtain data from
pages = ["https://www.blockchain.com/charts/total-bitcoins",
         "https://www.blockchain.com/charts/blocks-size",
         "https://www.blockchain.com/charts/hash-rate",
         "https://www.blockchain.com/charts/n-unique-addresses",
         "https://www.blockchain.com/charts/my-wallet-n-users"]

#List of related metrics to scrape for website section
currency_statistics = ["Total Circulating Bitcoin",
                      "Market Price (USD)",
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

#Scrape Currency Statistics
driver = webdriver.Chrome(driver_path, chrome_options = chrome_options)
driver.get(pages[0])

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
command_result = driver.execute("send_command", params)

for i in currency_statistics:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "*"):
        print("Moving " + j + " to git repo")
        shutil.move(j, repo_path + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Scrape Block Details
driver = webdriver.Chrome(driver_path, chrome_options = chrome_options)
driver.get(pages[1])

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
command_result = driver.execute("send_command", params)

for i in block_details:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "*"):
        print("Moving " + j + " to git repo")
        shutil.move(j, repo_path + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Scrape Mining Info
driver = webdriver.Chrome(driver_path, chrome_options = chrome_options)
driver.get(pages[2])

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
command_result = driver.execute("send_command", params)

for i in mining_info:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "*"):
        print("Moving " + j + " to git repo")
        shutil.move(j, repo_path + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Scrape Network Activity
driver = webdriver.Chrome(driver_path, chrome_options = chrome_options)
driver.get(pages[3])

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
command_result = driver.execute("send_command", params)

for i in network_activity:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "*"):
        print("Moving " + j + " to git repo")
        shutil.move(j, repo_path + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")

#Scrape Wallet Activity
driver = webdriver.Chrome(driver_path, chrome_options = chrome_options)
driver.get(pages[4])

driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
command_result = driver.execute("send_command", params)

for i in wallet_activity:
    driver.find_element_by_link_text(i).click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[contains(.,'All Time')]").click()
    time.sleep(2)
    driver.find_element_by_xpath("//option[contains(.,'CSV Format')]").click()
    print("Exported " + i )
    time.sleep(2)
    
    for j in glob.glob(dl_path + "*"):
        print("Moving " + j + " to git repo")
        shutil.move(j, repo_path + i.replace(" ", "_").lower() + "_" + str(today) + ".csv")
