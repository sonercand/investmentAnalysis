import os
from re import L
import pandas as pd
from dotenv import load_dotenv
import requests
import json

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


res = getFundamental(symbol="AAPL", function="INCOME_STATEMENT")
df = formatFundamental(res)

print(df)

## income statements
