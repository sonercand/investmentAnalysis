from cmath import exp
from tkinter import W
import pandas as pd
import json
from Calculations.portfolioOptimisation import OptimisePortfolio
from multiprocessing import Pool, Process
import numpy as np

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

weightRange = [k for k in range(10)]
print(weightRange)
weights = []
from sklearn.model_selection import ParameterGrid

W = []
n_iter = 100000
k = 0
while k <= n_iter:
    k += 1
    weights = op.setRandomWeights(n=len(tickers))
    W.append(weights)
# print(W)

w = np.matrix(W)
print(w.shape, dr.mean().shape)
pReturnsAvg = np.dot(dr.mean(), w.T)
print(dr.head())
returns = np.dot(dr, w.T)
risk = returns.std(axis=1) * np.sqrt(252)
print(risk[risk > 0.2])
