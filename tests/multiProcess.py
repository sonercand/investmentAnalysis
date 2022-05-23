import pandas as pd
import json
from Calculations.portfolioOptimisation import OptimisePortfolio
from multiprocessing import Pool, Process, Manager
import multiprocessing as mp
import time
import numpy as np


def randomPortfolio(oP, n, expReturnsAnnual, covMatrix, return_dict):
    w = np.random.randint(0, 1000, n)
    w = w / np.sum(w)
    portfolioReturn = oP.portfolioReturns(weights=w, expReturnsAnnual=expReturnsAnnual)
    portRisk = oP.portfolioRisk(weights=w, covMatrix=covMatrix)
    sharpeRatio = portfolioReturn / portRisk

    return_dict.append(
        (
            portfolioReturn,
            portRisk,
            sharpeRatio,
        )
    )
    return return_dict


if __name__ == "__main__":
    # run in sequence -----------
    t1 = time.time()
    data = pd.read_csv("./data/snpFtseClose.csv")
    stocks0 = ["BATS.L", "IMB.L", "MO", "PM"]
    stocks = stocks0.copy()
    stocks.append("Date")
    data = data[stocks]
    risk = 0.1
    oP = OptimisePortfolio(
        data=data,
        period=3,
        risk=risk,
        objectFunction="Sharpe",
        useLogReturns=True,
    )
    dr, tickers, covMatrix = oP.processData()
    expectedAnnualReturns = oP.expectedAnnualReturns(dr)
    t2 = time.time()
    print(t2 - t1)
    tnull = time.time()
    manager = Manager()
    return_dict = manager.list()
    n = len(stocks)
    jobs = []
    n_iter = 20
    for k in range(n_iter):
        p = Process(
            target=randomPortfolio,
            args=(oP, n - 1, expectedAnnualReturns, covMatrix, return_dict),
        )
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.terminate()
        # proc.join()

    t3 = time.time()
    print("it took to run algo {} times only {} seconds".format(n_iter, t3 - tnull))
    # print(return_dict.values())
    oP.genRandomPortfolios(expectedAnnualReturns, covMatrix, stocks0, n_iter)
    t4 = time.time()
    print()
    # print(return_dict)
    p.terminate()
