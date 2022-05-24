"""
Builds a portfolio using optimisation

data: pandas dataframe: dataset that contains ticker data for selected stocks. Its index is Date column, other columns have the ticker name, values are daily close values.

period: Int: Number of years to extract close values. Based on that period, daily returns are calculated and aggregated.

risk: Intended risk value. It can be a float or a list of float containing only the intended lowest risk and the highest risk.

objectFunction: String: Has only 2 possible values atm. These are "Returns" and "Sharpe Ratio". It is used to selected the function that will be optimised.

useLogReturns: bool: Instead of normal returns if set the True optimisation algorithm will use log of the returns.


example usage: 

        data = pd.read_csv("./data/snpFtseClose.csv")
        op = OptimisePortfolio(
            data=data, period=2, risk=[0.05, 0.2], objectFunction="Returns", useLogReturns=False
        )
        dr, tickers, covMatrix = op.processData()
        expectedAnnualReturns = op.expectedAnnualReturns(dr)

        res = op.maximizePortfolioReturns(covMatrix, tickers, expectedAnnualReturns)
        print(res)
        pr = op.portfolioReturns(res, expectedAnnualReturns)
        print(pr)
        pRisk = op.portfolioRisk(res, covMatrix)
        print(pRisk)

"""


import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.optimize import minimize


class OptimisePortfolio:
    def __init__(
        self,
        data,
        period,
        risk,
        useLogReturns=True,
        workDaysinYear=252,
        objectFunction="Sharpe",
    ):
        self.data = data
        self.period = period
        self.workDaysinYear = workDaysinYear
        self.useLogReturns = useLogReturns
        self.risk = risk
        self.useRiskRange = True if isinstance(risk, list) else False
        self.objectFunction = objectFunction

    def setUseLogReturns(self, val=False):
        self.useLogReturns = val

    def calculateLogReturn(self, data: pd.DataFrame):
        """return log returns"""
        return np.log(data / data.shift(1)).dropna()

    def calculateReturn(self, data: pd.DataFrame):
        """return percent daily return"""
        return data.pct_change(1).dropna()

    def expectedAnnualReturns(self, dr: pd.DataFrame) -> pd.Series:
        return dr.mean() * self.workDaysinYear

    def portfolioReturns(
        self, weights: np.ndarray, expReturnsAnnual: pd.DataFrame
    ) -> float:
        return np.sum(expReturnsAnnual * weights)

    def portfolioRisk(self, weights: np.ndarray, covMatrix: pd.DataFrame) -> float:
        varPort = np.dot(weights.T, np.dot(covMatrix, weights))
        try:
            stdPort = np.sqrt(varPort)
            stdPortAnnual = stdPort * np.sqrt(252)
            return stdPortAnnual
        except Exception as e:
            print(e, varPort, weights)

    def sharpeRatio(
        self,
        weights: np.ndarray,
        expReturnsAnnual: pd.DataFrame,
        covMatrix: pd.DataFrame,
    ) -> float:
        return self.portfolioReturns(
            weights=weights, expReturnsAnnual=expReturnsAnnual
        ) / self.portfolioRisk(weights, covMatrix)

    def sortinoRatio(self, weights, dailyReturns):
        """Like sharpe Ratio except replaces positive changes with zero so that optimisation focuses on reducing the negative variance"""

        downside = dailyReturns[dailyReturns < 0]
        d2 = downside * weights
        d3 = d2.sum(axis=1)

        sum_ = np.sum(dailyReturns.mean() * weights)

        return (252**0.5) * sum_ / d3.std()

    def setRandomWeights(self, n: int) -> np.ndarray:
        """arg: n: int: number of tickers"""
        w = np.random.randint(0, 10000, n) + 0.0001
        # w = np.random.random(n)
        return w / np.sum(w)

    def genRandomPortfolios(
        self,
        expReturnsAnnual: pd.DataFrame,
        covMatrix: pd.DataFrame,
        tickers: list,
        n_iter=3000,
    ) -> pd.DataFrame:
        """generate random portfolios and their risk and return values"""
        results = []
        setRandomWeights = self.setRandomWeights
        k = 0
        while k <= n_iter:
            k += 1
            weights = setRandomWeights(n=len(tickers))
            portfolioReturn = self.portfolioReturns(
                weights=weights, expReturnsAnnual=expReturnsAnnual
            )
            portRisk = self.portfolioRisk(weights=weights, covMatrix=covMatrix)
            res = {
                "weights": weights,
                "returns": portfolioReturn,
                "risk": portRisk,
                "sharpeRatio": portfolioReturn / portRisk,
            }
            results.append(res)
        output = pd.DataFrame(results)
        return output

    def removeNullCols(self, tickers):
        for col in tickers:
            percent_missing = self.data[col].isnull().sum() * 100 / len(self.data[col])
            if percent_missing > 70:  # remove ticks that have few data points
                tickers.remove(col)
        return tickers

    def processData(self):
        """returns dr, tickers,covMatrix"""
        tickers = list(self.data.columns)
        try:
            tickers.remove("index")
        except:
            print("dataset does not have redundant index column")
        try:
            tickers.remove("Date")
        except:
            print("Date coloumn not found")
        tickers = self.removeNullCols(tickers)
        currentDay = datetime.now()
        lastYearToday = currentDay - relativedelta(years=self.period)
        data = self.data[
            (pd.to_datetime(self.data["Date"]) > lastYearToday)
            & (pd.to_datetime(self.data["Date"]) < currentDay)
        ][tickers]
        if self.useLogReturns:
            dr = self.calculateLogReturn(data[tickers])  # log returns daily
        else:
            dr = self.calculateReturn(data[tickers])  # daily returns
        covMatrix = dr.cov()
        return dr, tickers, covMatrix

    def portfolioSharpeRatioObjFun(self, weights, expReturnsAnnual, covMatrix):
        return -1 * self.sharpeRatio(weights, expReturnsAnnual, covMatrix)

    def portfolioSortinoRatioObjFun(self, weights, dailyReturns):
        return -1 * self.sortinoRatio(weights, dailyReturns)

    def portfolioReturnsObjFun(self, weights, expReturnsAnnual):
        return -1 * self.portfolioReturns(weights, expReturnsAnnual)

    def sumofWeightsConstrait(self):
        return {
            "type": "eq",
            "fun": lambda x: np.sum(x) - 1,
        }

    def portfolioRiskRangeLBConstrait(self, weights, covMatrix, risk):
        min_ = self.risk[0]
        return self.portfolioRisk(weights, covMatrix) - min_

    def portfolioRiskRangeUBConstrait(self, weights, covMatrix, risk):
        max_ = self.risk[1]
        return max_ - self.portfolioRisk(weights, covMatrix)

    def portfolioRiskConstraint(self, weights, covMatrix, risk):
        calcRisk = self.portfolioRisk(weights, covMatrix)
        return calcRisk - risk

    def maximizePortfolioReturns(
        self, covMatrix, tickers, expectedAnnualReturns, dailyReturns, risk=None
    ):
        if risk == None:
            risk = self.risk

        if self.objectFunction == "Sharpe":
            objFun = self.portfolioSharpeRatioObjFun
            args = (expectedAnnualReturns, covMatrix)
        elif self.objectFunction == "Returns":
            objFun = self.portfolioReturnsObjFun
            args = expectedAnnualReturns
        elif self.objectFunction == "Sortino":
            objFun = self.portfolioSortinoRatioObjFun
            args = dailyReturns
        else:
            print("Object function should be either Sharpe or Returns")
        constraits = []
        constraits.append(self.sumofWeightsConstrait())
        if self.useRiskRange:
            constraits.append(
                {
                    "type": "ineq",
                    "fun": self.portfolioRiskRangeLBConstrait,
                    "args": (covMatrix, risk),
                }
            )
            constraits.append(
                {
                    "type": "ineq",
                    "fun": self.portfolioRiskRangeUBConstrait,
                    "args": (covMatrix, risk),
                }
            )
        else:
            constraits.append(
                {
                    "type": "eq",
                    "fun": self.portfolioRiskConstraint,
                    "args": (covMatrix, risk),
                }
            )
        bounds = tuple((0, 1) for _ in range(len(tickers)))
        initialWeights = np.ones(len(tickers)) / len(
            tickers
        )  # self.setRandomWeights(len(tickers))
        result = minimize(
            fun=objFun,
            x0=initialWeights,
            args=args,
            method="SLSQP",
            bounds=bounds,
            constraints=constraits,
        )

        return result["x"]
