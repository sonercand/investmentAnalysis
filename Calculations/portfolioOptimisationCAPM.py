from cmath import exp
from re import L
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.optimize import minimize
import time


def processData(data, esgData, expectedQuarReturns, tickers, period=2):
    tickers = [stock.upper() for stock in tickers]

    currentDay = datetime.now()
    lastYearToday = currentDay - relativedelta(years=period)
    # data["Date"] = data.index
    data.index = pd.to_datetime(data.index)
    data.dropna(axis=1, how="all", inplace=True)
    # data.set_index("Date", inplace=True)
    data.sort_index(inplace=True)
    data = data[
        (pd.to_datetime(data.index) > lastYearToday)
        & (pd.to_datetime(data.index) < currentDay)
    ][tickers]

    data = data.resample("M").last()
    monthlyLogReturns = np.log(data / data.shift(1))[1:]
    print(monthlyLogReturns)
    monthlyLogReturns.fillna(method="bfill", inplace=True)
    covMatrix = monthlyLogReturns.cov()
    esgData = esgData[tickers]
    expectedQuarReturns = expectedQuarReturns[expectedQuarReturns.ticker.isin(tickers)]
    expectedQuarReturns.fillna(-1, inplace=True)
    return data, monthlyLogReturns, covMatrix, esgData, expectedQuarReturns


def portfolioReturn(data, expectedQuarReturns, weights):
    k = 0
    sum_ = 0
    for ticker in data.columns:
        ret = expectedQuarReturns[expectedQuarReturns.ticker == ticker][
            "expectedReturn"
        ].values[0]
        sum_ += ret * weights[k]

        k += 1

    return sum_


def portfolioRisk(covMatrix, weights):
    varPort = np.dot(weights.T, np.dot(covMatrix, weights))

    try:
        stdPort = np.sqrt(varPort)
        stdPortAnnual = stdPort * np.sqrt(12)

        return stdPortAnnual
    except Exception as e:
        print(e, varPort, weights)


def portfolioESGscore(weights, esgData):
    return np.dot(esgData, weights)[0]


def sharpeRatio(data, weights, expectedQuarReturns, covMatrix):
    return portfolioReturn(data, expectedQuarReturns, weights) / portfolioRisk(
        covMatrix, weights
    )


def portfolioSharpeRatioObjFun(weights, data, expectedQuarReturns, covMatrix):
    return -1 * sharpeRatio(
        weights=weights,
        data=data,
        expectedQuarReturns=expectedQuarReturns,
        covMatrix=covMatrix,
    )


def sumofWeightsConstrait():
    return {
        "type": "eq",
        "fun": lambda x: np.sum(x) - 1,
    }


def portfolioESGConstrait(weights, esgScore, esgData):
    """constrait: esgValue of Portfolio should be larger than the esgScore set by user"""
    esgValue = portfolioESGscore(weights, esgData)
    return esgValue - esgScore


def portfolioRiskRangeLBConstrait(weights, covMatrix, risk):
    min_ = risk[0]
    return portfolioRisk(covMatrix, weights) - min_


def portfolioRiskRangeUBConstrait(weights, covMatrix, risk):
    max_ = risk[1]
    return max_ - portfolioRisk(covMatrix, weights)


def portfolioRiskConstraint(weights, covMatrix, risk):
    calcRisk = portfolioRisk(covMatrix, weights)
    return calcRisk - risk


def maximizePortfolioReturns(
    data,
    covMatrix,
    tickers,
    expectedQuarReturns,
    risk=None,
    esgScore=None,
    esgData=None,
):
    objFun = portfolioSharpeRatioObjFun
    args = (data, expectedQuarReturns, covMatrix)
    constraits = []
    constraits.append(sumofWeightsConstrait())
    if esgScore != None:
        constraits.append(
            {
                "type": "ineq",
                "fun": portfolioESGConstrait,
                "args": (esgScore, esgData),
            }
        )
    if isinstance(risk, list):
        constraits.append(
            {
                "type": "ineq",
                "fun": portfolioRiskRangeLBConstrait,
                "args": (covMatrix, risk),
            }
        )
        constraits.append(
            {
                "type": "ineq",
                "fun": portfolioRiskRangeUBConstrait,
                "args": (covMatrix, risk),
            }
        )
    else:
        constraits.append(
            {
                "type": "eq",
                "fun": portfolioRiskConstraint,
                "args": (covMatrix, risk),
            }
        )
    bounds = tuple((0, 1) for _ in range(len(tickers)))
    initialWeights = np.ones(len(tickers)) / len(
        tickers
    )  # self.setRandomWeights(len(tickers))
    print("started optimisation")
    t1 = time.time()
    result = minimize(
        fun=objFun,
        x0=initialWeights,
        args=args,
        method="SLSQP",
        bounds=bounds,
        constraints=constraits,
    )
    print("optimisation ended")
    print("seconds it took: ")
    print(time.time() - t1)
    return result["x"]


def setRandomWeights(n: int) -> np.ndarray:
    """arg: n: int: number of tickers"""
    # w = np.random.randint(0, 1000, n)
    w = np.random.random(n)
    return w / np.sum(w)


def genRandomPortfolios(
    data, expectedQuarReturns, tickers, covMatrix, n_iter=10000
) -> pd.DataFrame:
    """generate random portfolios and their risk and return values"""
    results = []
    k = 0
    while k <= n_iter:
        k += 1
        weights = setRandomWeights(n=len(tickers))
        Pret = portfolioReturn(
            data, weights=weights, expectedQuarReturns=expectedQuarReturns
        )
        Prisk = portfolioRisk(weights=weights, covMatrix=covMatrix)
        res = {
            "weights": weights,
            "returns": Pret,
            "risk": Prisk,
            "sharpeRatio": Pret / Prisk,
        }
        results.append(res)
    output = pd.DataFrame(results)
    return output


"""
##example
tickers = ["mng.l", "PRU.L", "AAPL", "MSFT"]
data = pd.read_csv("./data/snpFtseClose.csv")
expectedQuarReturns = pd.read_csv("./data/expectedReturns4monthlyCAPM.csv")
esgData = pd.read_csv("./data/esgScores_aligned.csv")
risk = [0, 1]
data, monthlyLogReturns, covMatrix, esgData, expectedQuarReturns = processData(
    data, esgData, expectedQuarReturns, tickers
)


optW = maximizePortfolioReturns(
    data, covMatrix, tickers, expectedQuarReturns, risk
).round(2)
optRisk = portfolioRisk(covMatrix=covMatrix, weights=optW)
optRet = portfolioReturn(data, expectedQuarReturns=expectedQuarReturns, weights=optW)


randP = genRandomPortfolios(
    data=data, expectedQuarReturns=expectedQuarReturns, tickers=tickers
)
"""
