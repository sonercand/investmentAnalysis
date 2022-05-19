import pandas as pd
import json
from Calculations.portfolioOptimisation import OptimisePortfolio


riskRange = [0, 0.4]
data = pd.read_csv("./data/snpFtseClose.csv")
print(data)
sectors = ["BATS.L", "IMB.L", "MO", "PM"]
sectors = [sectors]
stocks = [item for sublist in sectors for item in sublist]
print(stocks)
stocks.append("Date")
data = data[stocks]
op = OptimisePortfolio(
    data=data,
    period=3,
    risk=riskRange,
    objectFunction="Sharpe",
    useLogReturns=True,
)
dr, tickers, covMatrix = op.processData()
expectedAnnualReturns = op.expectedAnnualReturns(dr)
optWeights = op.maximizePortfolioReturns(
    covMatrix, tickers, expectedAnnualReturns
).round(4)
pr = op.portfolioReturns(optWeights, expectedAnnualReturns)
pRisk = op.portfolioRisk(optWeights, covMatrix)
print(pr, pRisk)
print(len(tickers), len(optWeights))
list_ = list(zip(tickers, optWeights))
print(list_)


def takeSecond(elem):
    return elem[1]


list_.sort(key=takeSecond, reverse=True)
print(list_)
