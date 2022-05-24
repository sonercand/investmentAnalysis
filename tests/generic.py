from cmath import exp
import pandas as pd
import json
from Calculations.portfolioOptimisation import OptimisePortfolio
from multiprocessing import Pool, Process


riskRange = [0, 0.4]
data = pd.read_csv("./data/snpFtseClose.csv")

sectors = ["BATS.L", "IMB.L", "MO", "PM"]
sectors = [sectors]
stocks = [item for sublist in sectors for item in sublist]

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
downside = dr[dr > 0]
weights = [0.25, 0.25, 0.25, 0.25]
print(dr.head())
d2 = downside * weights
d3 = d2.sum(axis=1)
print(dr.std())
print(d3.std())
print(d3.head())
print((252**0.5) * d3.mean() / d3.std())
