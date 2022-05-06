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

# Treasury Yield 10 Years (^TNX)


def getRiskFreeReturn(period):
    end = datetime.today()
    days = timedelta(period)
    start = end - days
    start = str(start.strftime("%Y-%m-%d"))
    end = str(end.strftime("%Y-%m-%d"))
    dfMarket = web.get_data_yahoo("^TNX", start, end, interval="m")
    return dfMarket["Close"].mean()
