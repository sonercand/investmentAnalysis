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

    def calculateLogReturn(self, data: pd.DataFrame):
        """return log returns"""
        return np.log(data / data.shift(1)).dropna(inplace=True)

    def calculateReturn(self, data: pd.DataFrame):
        return data.pct_change(1).dropna(inplace=True)

    def expectedAnnualReturns(self, dr: pd.DataFrame):
        """
        args:
            dr: pandas dataframe: daily returns for tickers
        returns:
            expReturnsAnnual: pandas dataframe:annualised returns where tickers are the dataframe index
        """
        expReturnsDaily = dr.mean()
        workDaysInYear = self.workDaysinYear
        expReturnsAnnual = ((1 + expReturnsDaily) ** (workDaysInYear)) - 1
        return expReturnsAnnual

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

    def setRandomWeights(self, n: int) -> np.ndarray:
        """arg: n: int: number of tickers"""
        w = np.random.random(n)
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

    def processData(self):
        data = self.data
        period = self.period
        useLogReturns = self.useLogReturns
        calculateLogReturn = self.calculateLogReturn
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
        else:
            dr = self.calculateReturn(data[tickers])  # daily returns
        covMatrix = dr.cov()
        return dr, tickers, covMatrix

    def portfolioSharpeRatioObjFun(self, weights, expReturnsAnnual, covMatrix):
        return -1 * self.sharpeRatio(weights, expReturnsAnnual, covMatrix)

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

    def maximizePortfolioReturns(self, covMatrix, tickers, expectedAnnualReturns):
        if self.objectFunction == "Sharpe":
            objFun = self.portfolioSharpeRatioObjFun
            args = (expectedAnnualReturns, covMatrix)
        elif self.objectFunction == "Returns":
            objFun = self.portfolioReturnsObjFun
            args = expectedAnnualReturns
        else:
            print("Object function should be either Sharpe or Returns")
        constraits = []
        constraits.append(self.sumofWeightsConstrait())
        if self.useRiskRange:
            constraits.append(
                {
                    "type": "ineq",
                    "fun": self.portfolioRiskRangeLBConstrait,
                    "args": (covMatrix, self.risk),
                }
            )
            constraits.append(
                {
                    "type": "ineq",
                    "fun": self.portfolioRiskRangeUBConstrait,
                    "args": (covMatrix, self.risk),
                }
            )
        else:
            constraits.append(
                {
                    "type": "eq",
                    "fun": self.portfolioRiskConstraint,
                    "args": (covMatrix, self.risk),
                }
            )
        bounds = tuple((0, 1) for _ in range(len(tickers)))
        initialWeights = self.setRandomWeights(len(tickers))
        result = minimize(
            fun=objFun,
            x0=initialWeights,
            args=args,
            method="SLSQP",
            bounds=bounds,
            constraints=constraits,
        )
        return result["x"].round(4)
