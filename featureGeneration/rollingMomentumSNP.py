"""Only for S&P500"""
import pandas as pd
import numpy as np
from statsmodels.regression.rolling import RollingOLS
import datetime
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


def momentum(ticker, data, window):
    subData = data[["Date", ticker]]
    subData.fillna(method="ffill", inplace=True)
    subData.dropna(inplace=True)
    momentum = np.full(len(subData), np.nan)
    alpha = np.full(len(subData), np.nan)
    for i in range(len(subData) - window):
        regressor = LinearRegression()
        x = subData.iloc[i : i + window + 1].index.values.reshape(-1, 1)
        y = subData.iloc[i : i + window + 1][ticker].values.reshape(-1, 1)

        regressor.fit(
            x,
            y,
        )
        momentum[i + window] = regressor.coef_[0]
        alpha[i + window] = regressor.intercept_[0]
        subData_ = subData[["Date"]]
        subData_[ticker] = momentum
        subData_.set_index("Date", inplace=True)
    return subData_


data = pd.read_csv(".\data\snpFtseClose.csv")  # adjusted close data
data["Date"] = data["Unnamed: 0"]
data.drop(["Unnamed: 0"], axis=1, inplace=True)
cols = list(data.columns)
cols = [col for col in cols if not col.upper().endswith(".L")]
data = data[cols]
data["Date"] = pd.to_datetime(data["Date"])
data.set_index("Date", inplace=True)
data.sort_index(inplace=True)
data = data.reset_index()
window = 13 * 7  # days ->  3 months which is 13 weeks.


tickers = list(pd.read_csv(".\data\snp500Components.csv")["Symbol"].values)
save_ = "./data/momentumSNP.csv"
dfs = []
k = 0
for ticker in tickers:
    try:
        df = momentum(ticker=ticker, data=data, window=window)
        dfs.append(df)
    except Exception as e:
        print(e)
        print(ticker)


out_ = pd.concat(dfs, axis=1)
out_.to_csv(save_)
