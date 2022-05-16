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
from pickletools import optimize
from matplotlib import ticker
from calcExpectedReturn import getExpectedReturn
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.optimize import minimize


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


def sharpeRatio(weights, expReturnsAnnual, covMatrix):
    return portfolioReturns(
        weights=weights, expReturnsAnnual=expReturnsAnnual
    ) / portfolioRisk(weights, covMatrix)


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


def portfolioRiskConstraint(weights, covMatrix, risk):
    calcRisk = portfolioRisk(weights, covMatrix)
    return calcRisk - risk


def portfolioRiskConstraintRangeLB(weights, covMatrix, minRisk):
    min_ = minRisk
    calcRisk = portfolioRisk(weights, covMatrix)
    return calcRisk - min_  # calcRisk>min_


def portfolioRiskConstraintRangeUB(weights, covMatrix, maxRisk):
    max_ = maxRisk
    calcRisk = portfolioRisk(weights, covMatrix)
    return max_ - calcRisk  # -calcRisk+max_


def portfolioReturnsObjFun(weights, expReturnsAnnual):
    return -1 * portfolioReturns(weights=weights, expReturnsAnnual=expReturnsAnnual)


def portfolioSharpeRatioObjFun(weights, expReturnsAnnual, covMatrix):
    return -1 * sharpeRatio(weights, expReturnsAnnual, covMatrix)


# portfolio optimisation for a given risk range


def maximisePortfolioReturnRange(covMatrix, riskRange, tickers, expectedAnnualReturns):
    constraintA = {
        "type": "eq",
        "fun": lambda x: np.sum(x) - 1,
    }  # sum of the weights = 1
    constraintB = {
        "type": "ineq",
        "fun": portfolioRiskConstraintRangeLB,
        "args": (covMatrix, riskRange[0]),
    }
    constraintC = {
        "type": "ineq",
        "fun": portfolioRiskConstraintRangeUB,
        "args": (covMatrix, riskRange[1]),
    }
    bounds = tuple((0, 1) for _ in range(len(tickers)))
    initialWeights = setRandomWeights(len(tickers))
    result = minimize(
        fun=portfolioReturnsObjFun,
        x0=initialWeights,
        args=expectedAnnualReturns,
        method="SLSQP",
        bounds=bounds,
        constraints=[constraintA, constraintB, constraintC],
    )
    return result["x"]


# portfolio optimisation for a given risk value
def maximisePortfolioReturn(covMatrix, risk, tickers, expectedAnnualReturns):
    constraintA = {
        "type": "eq",
        "fun": lambda x: np.sum(x) - 1,
    }  # sum of the weights = 1
    constraintB = {
        "type": "eq",
        "fun": portfolioRiskConstraint,
        "args": (covMatrix, risk),
    }
    bounds = tuple((0, 1) for _ in range(len(tickers)))
    initialWeights = setRandomWeights(len(tickers))
    result = minimize(
        fun=portfolioReturnsObjFun,
        x0=initialWeights,
        args=expectedAnnualReturns,
        method="SLSQP",
        bounds=bounds,
        constraints=[constraintA, constraintB],
    )
    return result["x"].round(3)


data = pd.read_csv("./data/snpFtseClose.csv")
dr, tickers, covMatrix = processData(data=data, period=2, useLogReturns=True)
print(dr.head())

eAR = expectedAnnualReturns(dr)
print(eAR.loc["AAPL"])
eAR = expectedAnnualReturns(dr)
dfR = randomSolve(eAR, covMatrix=covMatrix, tickers=tickers)
print(dfR.head())
risk = [0.01, 0.2]
result = maximisePortfolioReturnRange(
    covMatrix, risk, tickers, expectedAnnualReturns=eAR
)
print(result)
print(portfolioRisk(result, covMatrix))
print(portfolioReturns(weights=result, expReturnsAnnual=eAR))
