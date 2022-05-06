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
from calcBeta import calculateBeta
from calcRiskFreeReturn import getRiskFreeReturn
from calcExpectedReturn import getExpectedReturn
from datetime import datetime, timedelta
import pandas_datareader as web


marketTic = "^GSPC"
end = datetime.today()
# end = datetime(2021, 12, 30)
days = timedelta(365)
start = end - days
# start = datetime(2021, 1, 1)
start = str(start.strftime("%Y-%m-%d"))
end = str(end.strftime("%Y-%m-%d"))

dfMarket = web.get_data_yahoo(marketTic, start, end)
dfMarket.dropna(inplace=True)
expectedReturnMarket = getExpectedReturn(dfMarket, "Close")
print(expectedReturnMarket)

riskFreeRate = getRiskFreeReturn(1) / 100
print(riskFreeRate)

stockTic = "MSFT"
beta = calculateBeta(stockTic=stockTic, marketTic=marketTic, period=1)
print(beta)

expectedReturnTic = riskFreeRate + beta * (expectedReturnMarket - riskFreeRate)
print(expectedReturnTic * 100)
