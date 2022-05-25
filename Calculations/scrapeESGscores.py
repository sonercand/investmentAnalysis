"""
Use: company names to search on https://www.sustainalytics.com/esg-rating/british-american-tobacco-p-l-c and https://www.sustainalytics.com/esg-rating https://www.msci.com/research-and-insights/esg-ratings-corporate-search-tool
Use selenium, beautiful soup
collect values once.
"""
import re
from selenium import webdriver
from dotenv import load_dotenv
import os
import yfinance as yf
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import requests
import time
import numpy as np

load_dotenv()


def get_rawScore(
    searchBoxId,
    searchResultsListID,
    searchURL,
    ticker,
    delay=1,
    ratingSel=".ratingdata-company-rating",
):
    options = Options()
    options.headless = False
    driver = webdriver.Firefox(
        options=options, executable_path=os.getenv("geckodriver_PATH")
    )
    driver.get(searchURL)
    driver.maximize_window()
    if ticker.lower().endswith(".l"):
        ticker1 = ticker[:-2].upper()
    else:
        ticker1 = ticker
    driver.find_element(by=By.ID, value=searchBoxId).send_keys(
        ticker1
    )  # type ticker into search
    time.sleep(delay + 1)
    try:
        listItems = driver.find_element(by=By.CSS_SELECTOR, value=searchResultsListID)
        listItems.click()
    except Exception as e:
        # driver.close()
        print(e)
    time.sleep(delay)
    try:
        rate = (
            driver.find_element(by=By.CSS_SELECTOR, value=ratingSel)
            .get_attribute("Class")[-3:]
            .replace("-", "")
        )
    except Exception as e:
        driver.close()
        print(e)
    finally:
        driver.close()
    return rate


tickers = list(pd.read_csv("./data/snpFtseClose.csv").columns)
tickers.remove("Date")
print(tickers)
rates = []
k = 0
print(len(tickers))
print(len(tickers) % 4)
tickers_not_found = []
processed = pd.read_csv("./data/esg_ratings_raw.csv")
print(processed.shape)
processed = processed[["ticker", "rate"]].drop_duplicates()
processed.to_csv("./data/esg_ratings_raw.csv", index=False)
print(processed.shape)
tickers_processed = list(processed.ticker)
ta = set(tickers)
tpa = set(tickers_processed)
remaining = ta - tpa
print(len(remaining), len(tickers), len(tickers_processed))
remaining = list(remaining)

while len(remaining) > 0:
    ticker = remaining.pop(0)
    ticker0 = ticker
    if ticker == "A":
        ticker = "Agilent"
    elif ticker.upper() == "AAF.L":
        ticker = "AIRTEL"
    elif ticker.upper() == "ABC":
        ticker = "AmerisourceBergen"
    elif ticker.upper() == "ALK":
        ticker = "Alaska Air Group"
    print(ticker)
    print(k)
    try:
        rate = get_rawScore(
            searchBoxId="_esgratingsprofile_keywords",
            searchResultsListID="#ui-id-1",
            searchURL="https://www.msci.com/research-and-insights/esg-ratings-corporate-search-tool",
            ticker=ticker,
            delay=1,
        )
    except:
        tickers_not_found.append(ticker0)
        continue
    print(rate)
    if rate == "ea":
        rate = "a"
    k += 1
    rates.append({"ticker": ticker0, "rate": rate})

    if k % 4 == 0:
        dfT = pd.DataFrame(rates)
        dfT.to_csv("./data/esg_ratings_raw.csv", index=False, mode="a", header=False)
        rates = []
    print(tickers_not_found)
