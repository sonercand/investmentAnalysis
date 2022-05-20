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


def optWeights(oP, covMatrix, tickers, expectedAnnualReturns, results):
    optWeightsS = oP.maximizePortfolioReturns(
        covMatrix, tickers, expectedAnnualReturns, risk=0.1
    )
    results.append(optWeightsS)
    return results


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
    optWeightsS = oP.maximizePortfolioReturns(
        covMatrix, tickers, expectedAnnualReturns, risk=0.1
    )
    manager = Manager()
    results = manager.list()
    return_dict = manager.list()
    optWeights(oP, covMatrix, tickers, expectedAnnualReturns, results)
    args = (oP, covMatrix, tickers, expectedAnnualReturns, results)
    p1 = Process(
        target=optWeights,
        args=args,
    )
    p2 = Process(
        target=oP.genRandomPortfolios,
        args=(expectedAnnualReturns, covMatrix, stocks0, 1000),
    )
    p1.start()
    p2.start()
    p1.terminate()
    p2.terminate()
    p1.join()
    p2.join()
    t2 = time.time()
    print(t2 - t1)
    tnull = time.time()
    print(results)
