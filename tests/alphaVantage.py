import os
from re import L
import pandas as pd
from dotenv import load_dotenv
import requests
import json
import time

""" most of the functions work only for US stocks"""
load_dotenv()
api_key = os.getenv("ALPHAVANTAGE_API_KEY")


def getFundamental(symbol, function="INCOME_STATEMENT", api_key=api_key):
    url = "https://www.alphavantage.co/query?function={}&symbol={}&apikey={}".format(
        function, symbol, api_key
    )
    return requests.get(url).json()


def formatFundamental(dict_):
    ticker = dict_["symbol"]
    df = pd.DataFrame(dict_["annualReports"])
    df["ticker"] = ticker
    return df


## Load INCOME STATEMENTS ##############################################
tickers = list(pd.read_csv(".\data\snp500Components.csv")["Symbol"].values)
m = 0
maxRequestsPerMin = 5
try:
    getAlreadySavedTickers = list(
        pd.read_csv(".\data\income_statementsSNP.csv")["ticker"].values
    )
except Exception as e:
    print(e)
    getAlreadySavedTickers = []
remaining = set(tickers) - set(getAlreadySavedTickers)
queue = list(remaining).copy()
print(len(queue), len(getAlreadySavedTickers), len(tickers))

while queue:
    t1 = time.time()
    ticker = queue.pop()
    try:
        res = getFundamental(symbol=ticker, function="INCOME_STATEMENT")
        t2 = time.time()
        if t2 - t1 < 60 / maxRequestsPerMin:
            time.sleep(12 + 1 - (t2 - t1))

    except Exception as e:
        print("--------getFundamenta failed----")
        print(e)
        print(ticker)
        print(res)
    try:
        df = formatFundamental(res)
    except Exception as e:
        print("format fundamental failed")
        print(e, ticker, res)

    mode = "w" if m == 0 and len(getAlreadySavedTickers) == 0 else "a"
    header = True if m == 0 and len(getAlreadySavedTickers) == 0 else False
    try:
        df.to_csv(
            "./data/income_statementsSNP.csv", index=False, mode=mode, header=header
        )
    except Exception as e:
        print(e)
        print(ticker, m)
        continue
    m += 1

## income statements
