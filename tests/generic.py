from cmath import exp
from tkinter import W
from xml.sax.xmlreader import IncrementalParser
import pandas as pd
import json
from Calculations.portfolioOptimisation import OptimisePortfolio
from multiprocessing import Pool, Process
import numpy as np
import yfinance as yf

riskRange = [0, 0.4]
data = pd.read_csv("./data/snpFtseClose.csv")

stockDict = {
    "REL.L": 0.4279875,
    "GOOGL": 0.1851415,
    "PSON.L": 0.1309079,
    "AUTO.L": 0.1136884,
    "RMV.L": 0.0437663,
    "WPP.L": 0.0268633,
    "GOOG": 0.0261879,
    "FB": 0.0217533,
    "ITV.L": 0.0177287,
    "MTCH": 0.0059754,
}
stocks_and_date = list(stockDict.keys())
stocks_and_date.append("Date")

dataPort = data[stocks_and_date]
dataPort.set_index("Date", inplace=True)
dataPort.sort_index(inplace=True)
cum_res = (dataPort.pct_change(1) + 1).cumprod()
cum_res.dropna(inplace=True)
array_ = []
for k, v in stockDict.items():
    ll = np.ones(len(cum_res[k])) * v
    array_.append(cum_res[k] * ll)
res = pd.concat(array_, axis=1)
port_cumilative_returns = res.sum(axis=1)
print(port_cumilative_returns)
print(cum_res)
# ftse ^FTSE
# snp500 ^GSPC
ftseData = yf.download("^FTSE", "2017-05-26", "2022-05-25")
ftseData = ftseData["Adj Close"]
ftseCumRet = (ftseData.pct_change(1) + 1).cumprod()
ftseCumRet.dropna(inplace=True)
snpData = yf.download("^GSPC", "2017-05-26", "2022-05-25")
snpData = snpData["Adj Close"]
snpCumRet = (snpData.pct_change(1) + 1).cumprod()
snpCumRet.dropna(inplace=True)
print(snpCumRet)
print(ftseCumRet)


def transform(df):
    df = (df.pct_change(1) + 1).cumprod()
    df.dropna(inplace=True)
    return df
