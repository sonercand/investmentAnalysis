"""
TODO:
Return a portfolio with an optimum stock coefficients array that maximizes return min. risk

how: 
pre: calculate expected return for each component and store it
1) Random Path
dictionary[return,risk] = coefficients
k=100000
while m<k:
    select random coef. for each stock item where each coef is between 0 and 100
    normalise coef so that sum is equal to 1
    calc estimated return and estimated risk
    dictionary[(return,risk)] = current coefficients

For a given risk "apetite" say range between 0-10% select the max return then return the coeff belong to that return.
2) use optimiser algorithm (markowitz model specifically)
2) Using grid search
cascaded loops for each coef. (might take too long to calculate)


"""
from matplotlib import ticker
from calcExpectedReturn import getExpectedReturn
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta


def calculateLogReturn(data):
    return np.log(data / data.shift(1))


def processData(data, period=2, useLogReturns=True):
    data.reset_index(inplace=True)
    data["Date"] = pd.to_datetime(data.Date)
    tickers = list(data.columns)
    tickers.remove("index")
    tickers.remove("Date")
    for col in tickers:
        percent_missing = data[col].isnull().sum() * 100 / len(data[col])
        if percent_missing > 70:  # remove ticks that have few data points
            tickers.remove(col)
    currentDay = datetime.now()
    lastYearToday = currentDay - relativedelta(years=period)
    data = data[
        (pd.to_datetime(data["Date"]) > lastYearToday)
        & (pd.to_datetime(data["Date"]) < currentDay)
    ]
    if useLogReturns:
        dr = calculateLogReturn(data[tickers])  # log returns daily
        dr.dropna(inplace=True)
    else:
        dr = data[tickers].pct_change(1).dropna()  # daily returns
    covMatrix = dr.cov()
    return dr, tickers, covMatrix


def expectedAnnualReturns(dr):
    expReturnsDaily = dr.mean()
    workDaysInYear = 252
    expReturnsAnnual = ((1 + expReturnsDaily) ** (workDaysInYear)) - 1
    return expReturnsAnnual


def portfolioReturns(weights, expReturnsAnnual):
    return np.sum(expReturnsAnnual * weights)


def portfolioRisk(weights, covMatrix):
    varPort = np.dot(weights.T, np.dot(covMatrix, weights))
    try:
        stdPort = np.sqrt(varPort)
        stdPortAnnual = stdPort * np.sqrt(252)
        return stdPortAnnual
    except Exception as e:
        print(e, varPort, weights)


def setRandomWeights(n):
    w = np.random.random(n)
    return w / np.sum(w)


def randomSolve(expReturnsAnnual, covMatrix, tickers, n_iter=3000):
    results = []
    k = 0
    while k <= n_iter:
        k += 1
        weights = setRandomWeights(n=len(tickers))
        portfolioReturn = portfolioReturns(
            weights=weights, expReturnsAnnual=expReturnsAnnual
        )
        portRisk = portfolioRisk(weights=weights, covMatrix=covMatrix)
        res = {
            "weights": weights,
            "returns": portfolioReturn,
            "risk": portRisk,
            "sharpeRatio": portfolioReturn / portRisk,
        }
        results.append(res)
    output = pd.DataFrame(results)
    return output


data = pd.read_csv("./data/snpFtseClose.csv")
dr, tickers, covMatrix = processData(data=data, period=5, useLogReturns=True)
print(dr.head())

eAR = expectedAnnualReturns(dr)
print(eAR.loc["AAPL"])
eAR = expectedAnnualReturns(dr)
dfR = randomSolve(eAR, covMatrix=covMatrix, tickers=tickers)
print(dfR.head())
