"""
Expected returns using CAPM

E[rj] = rf +Bj(E[rm]-rf) where 
    E[rj] = Expected return on a stock j
    E[rm] = Expected retrun on the market
    rf = risk free rate (e.g. yield of bonds)
    Bj = Systematic risk of stock j

Bj = Covariance/Variance where
    Covariance = Measure of a stocks's return relative to that of the market
    Variance = Measure of how the market moves relative to its mean

"""
import pandas_datareader as web
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


def calculateBeta(stockTic, marketTic, period, usingLogReturns=False):
    """
    args:
        stockTic : string
        marketTic: string: ticker for the market e.g. ^GSPC
        period: int: number of years
    returns:
        beta float
    """
    end = datetime.today()
    days = timedelta(365 * period)
    start = end - days
    start = str(start.strftime("%Y-%m-%d"))
    end = str(end.strftime("%Y-%m-%d"))
    dfMarket = web.get_data_yahoo(marketTic, start, end, interval="m")
    dfMarket.dropna(inplace=True)
    df1 = web.get_data_yahoo(stockTic, start, end, interval="m")
    df1.dropna(inplace=True)
    if usingLogReturns:
        df1["returns_log"] = np.log(df1["Close"] / df1["Close"].shift())
        dfMarket["returns_log"] = np.log(dfMarket["Close"] / dfMarket["Close"].shift())
        covariance = df1["returns_log"].cov(dfMarket["returns_log"])
        variance = dfMarket["returns_log"].var()

    else:
        df1["returns"] = df1["Close"].pct_change(1)
        dfMarket["returns"] = dfMarket["Close"].pct_change(1)
        covariance = df1["returns"].cov(dfMarket["returns"])
        variance = dfMarket["returns"].var()
    beta = covariance / variance
    return beta


if __name__ == "__main__":
    stockTic = "AAPL"
    marketTic = "^GSPC"
    period = 2
    beta = calculateBeta(stockTic, marketTic, period, usingLogReturns=False)
    print(beta)
