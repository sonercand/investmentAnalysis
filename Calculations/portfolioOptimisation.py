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

2) Using grid search
cascaded loops for each coef. (might take too long to calculate)


"""
from unittest import result
from calcExpectedReturn import getExpectedReturn
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta


def processData(data, period=2):
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
    dr = data[tickers].pct_change(1).dropna()  # daily returns
    covMatrix = dr.cov()
    return dr, tickers, covMatrix


def expectedAnnualReturns(dr):
    expReturnsDaily = dr.mean()
    workDaysInYear = 250
    expReturnsAnnual = ((1 + expReturnsDaily) ** (workDaysInYear)) - 1
    return expReturnsAnnual


def setRandomWeights(n):
    rawWeights = np.random.randint(0, 1000, size=n)
    return rawWeights / np.sum(rawWeights)


data = pd.read_csv("./data/snpFtseClose.csv")
global covMatrix
dr, tickers, covMatrix = processData(data, 2)
global expReturnsAnnual
expReturnsAnnual = expectedAnnualReturns(dr)


def portfolioReturns(weights, expReturnsAnnual=expReturnsAnnual):
    return np.dot(np.transpose(weights), expReturnsAnnual)


def portfolioRisk(weights, covMatrix=covMatrix):
    varPort = np.dot(weights, np.dot(covMatrix, np.transpose(weights)))
    try:
        stdPort = np.sqrt(varPort)
        stdPortAnnual = stdPort * np.sqrt(250)
        return stdPortAnnual
    except Exception as e:
        print(e, varPort, weights)


def randomSolve(expReturnsAnnual, covMatrix, tickers, n_iter=3000):
    results = []
    k = 0
    while k <= n_iter:
        k += 1
        weights = setRandomWeights(n=len(tickers))
        portfolioReturn = portfolioReturns(expReturnsAnnual, weights)
        portRisk = portfolioRisk(covMatrix, weights)
        res = {
            "weights": weights,
            "returns": portfolioReturn,
            "risk": portRisk,
        }
        results.append(res)
    output = pd.DataFrame(results)
    return output


output = randomSolve(expReturnsAnnual, covMatrix, tickers)
print(output)
import matplotlib.pyplot as plt

# plt.scatter(output["returns"], output["risk"])
# plt.show()

from scipy.optimize import minimize


def optimize(tickers, target_return=0.35):
    init_guess = np.transpose(np.ones(len(tickers)) * (1.0 / len(tickers)))
    bounds = ((0.0, 1.0),) * len(tickers)
    weights = minimize(
        portfolioRisk,
        init_guess,
        method="SLSQP",
        options={"disp": False},
        constraints=(
            {"type": "eq", "fun": lambda inputs: 1.0 - np.sum(inputs)},
            {
                "type": "eq",
                "fun": lambda inputs: target_return - portfolioReturns(weights=inputs),
            },
        ),
        bounds=bounds,
    )
    return weights.x


res = optimize(tickers, target_return=0.20)
print(res)
"""
@TODO: check matrix multiplications as to find why portfolio risk is an array as an output from portfolio risk function

"""
