from audioop import avg
from turtle import st
from Calculations.portfolioOptimisation import OptimisePortfolio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# set up data
global stocks
stocks = ["A", "B", "C"]
global closeValues
closeValues = {
    "A": [100, 100, 100, 100],
    "B": [100, 110, 220, 220 * 4],
    "C": [1, 2, 4, 8],
    "Date": [
        datetime(2022, 1, 1),
        datetime(2022, 1, 2),
        datetime(2022, 1, 3),
        datetime(2022, 1, 4),
    ],
}
global data
data = pd.DataFrame(closeValues)


def setObject(useLogReturns=True):
    return OptimisePortfolio(
        data,
        1,
        risk=[0.2, 0.5],
        useLogReturns=useLogReturns,
        workDaysinYear=252,
        objectFunction="Sharpe",
    )


def test_init():
    op = setObject()
    pd.testing.assert_frame_equal(op.data, data)
    assert op.useRiskRange == True


def test_processData_logs():
    op = setObject()
    op.useLogReturns = True
    dr, tickers, covMatrix = op.processData()
    pd.testing.assert_frame_equal(covMatrix, dr.cov())
    dra = np.log(data[stocks] / data[stocks].shift(1)).dropna()
    print(covMatrix)
    print(dra.cov())
    pd.testing.assert_frame_equal(dra.cov(), covMatrix)
    print(covMatrix)
    assert tickers == stocks


def test_processData():
    op1 = setObject(useLogReturns=False)
    dr, tickers, covMatrix = op1.processData()
    pd.testing.assert_frame_equal(covMatrix, dr.cov())
    dra = data[stocks].pct_change(1).dropna()
    pd.testing.assert_frame_equal(dra[stocks].cov(), covMatrix)

    assert tickers == stocks


def test_calculateLogReturn():
    from math import e

    closeValuesLR = {
        "A": [e, e**2, e**4, e**7],  # log(A/A.shift(1)) = [NaN,1,2,3]
        "B": [1, e, e, e**101],  # [NaN,1,0,100]
        "date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
        ],
    }
    dataLR = pd.DataFrame(closeValuesLR)
    op = OptimisePortfolio(
        dataLR,
        1,
        risk=[0.2],
        useLogReturns=True,
        workDaysinYear=252,
        objectFunction="Sharpe",
    )
    returnsLn = op.calculateLogReturn(dataLR[["A", "B"]])
    np.testing.assert_array_equal(
        returnsLn.values, [[1.0, 1.0], [2.0, 0.0], [3.0, 100.0]]
    )


def test_calculateReturn():
    op = setObject()
    returnsPct = op.calculateReturn(data[stocks]).round(3)
    expectedReturns = [[0.0, 0.1, 1.0], [0.0, 1.0, 1.0], [0.0, 3.0, 1.0]]
    for e, a in zip(returnsPct.values, expectedReturns):
        assert list(e) == list(a)


def test_expectedAnnualReturns():
    closeValuesLR = {
        "A": [
            1,
            1 + 0.001,
            1 + 0.001 + (1 + 0.001) * 0.001,
            1 + 0.001 + (1 + 0.001) * 0.001 + (1 + 0.001 + (1 + 0.001) * 0.001) * 0.001,
        ],  # avg daily return: 0.001
        "B": [
            100,
            101,
            101 + (101 * 0.01),
            101 + (101 * 0.01) + (101 + 101 * 0.01) * 0.01,
        ],  # avg daily return:0.01
        "c": [1000, 1000, 1000, 1000],  # avg daily return: 0
        "Date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
        ],
    }
    dataLR = pd.DataFrame(closeValuesLR)
    op = OptimisePortfolio(
        dataLR,
        1,
        risk=[0.2],
        useLogReturns=False,
        workDaysinYear=252,
        objectFunction="Sharpe",
    )

    dr, tickers, covMatrix = op.processData()
    assert list(dr.mean().values.round(3)) == list([0.001, 0.01, 0])
    expAR = op.expectedAnnualReturns(dr)
    assert list(expAR.round(3)) == list(np.array([0.001, 0.01, 0]) * 252)


def test_portfolioReturns():
    closeValuesLR = {
        "A": [
            1,
            1 + 0.001,
            1 + 0.001 + (1 + 0.001) * 0.001,
            1 + 0.001 + (1 + 0.001) * 0.001 + (1 + 0.001 + (1 + 0.001) * 0.001) * 0.001,
        ],  # avg daily return: 0.001
        "B": [
            100,
            101,
            101 + (101 * 0.01),
            101 + (101 * 0.01) + (101 + 101 * 0.01) * 0.01,
        ],  # avg daily return:0.01
        "c": [1000, 1000, 1000, 1000],  # avg daily return: 0
        "Date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
        ],
    }
    dataLR = pd.DataFrame(closeValuesLR)
    op = OptimisePortfolio(
        dataLR,
        1,
        risk=[0.2],
        useLogReturns=False,
        workDaysinYear=252,
        objectFunction="Sharpe",
    )
    dr, tickers, covMatrix = op.processData()
    expAR = op.expectedAnnualReturns(dr)
    # equal weights:
    weights = [1 / 3, 1 / 3, 1 / 3]
    avgDailyReturns = np.array([0.001, 0.01, 0])
    avgAnnualReturns = avgDailyReturns * 252
    assert np.mean(avgAnnualReturns).round(4) == op.portfolioReturns(
        weights, expAR
    ).round(4)
    print(np.mean(avgAnnualReturns))
    # only stock c:
    weights = [0, 0, 1.0]
    assert 0 == op.portfolioReturns(weights, expAR).round(4)
    # only stock a:
    weights = [1, 0, 0]
    assert 0.001 * 252 == op.portfolioReturns(weights, expAR).round(4)
    # only stock b
    weights = [0, 1, 0]
    assert 0.01 * 252 == op.portfolioReturns(weights, expAR).round(4)


def test_portfolioRisk():
    closeValuesLR = {
        "A": [100, 101, 100, 101, 100],  # std  = 0.01
        "B": [1000, 1200, 960, 1152, 921.6],  # std = 0.2
        "C": [100, 100, 100, 100, 100],  # std= 0
        "Date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
            datetime(2022, 1, 5),
        ],
    }
    dataLR = pd.DataFrame(closeValuesLR)
    op = OptimisePortfolio(
        dataLR,
        1,
        risk=[0.2],
        useLogReturns=False,
        workDaysinYear=252,
        objectFunction="Sharpe",
    )

    dr, tickers, covMatrix = op.processData()
    # only C
    weights = np.array([0, 0, 1])
    pr = op.portfolioRisk(weights, covMatrix=covMatrix)
    assert pr == 0.0
    # only A
    weights = np.array([1, 0, 0])
    stdADaily = dr["A"].std()
    stdAAnnual = stdADaily * (252**0.5)
    pr = op.portfolioRisk(weights, covMatrix=covMatrix)
    assert pr.round(6) == stdAAnnual.round(6)
    # only B
    weights = np.array([0, 1, 0])
    pr = op.portfolioRisk(weights, covMatrix=covMatrix)
    stdADaily = dr["B"].std()
    stdAAnnual = stdADaily * (252**0.5)
    assert pr.round(6) == stdAAnnual.round(6)
    # equal weight
    weights = np.array([1 / 3, 1 / 3, 1 / 3])
    pr = op.portfolioRisk(weights, covMatrix=covMatrix)
    std = dr.std().mean() * (252**0.5)
    assert std == pr


def test_maximizePortfolioReturns():
    closeValuesLR = {
        "A": [1, 1, 1, 1, 1],  # zero risk zero return
        "B": [1000, 1200, 960, 1152, 921.6],  # risk = 0.053333, return 0
        "C": [100, 100, 100, 100, 100],  # zero risk zero return
        "D": [100, 101, 102, 101, 102],  # low risk  return 1.259878
        "E": [20, 23, 24, 18, 40],  # hight risk high return
        "Date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
            datetime(2022, 1, 5),
        ],
    }
    dataLR = pd.DataFrame(closeValuesLR)
    op = OptimisePortfolio(
        dataLR,
        1,
        risk=0,
        useLogReturns=False,
        workDaysinYear=252,
        objectFunction="Sharpe",
    )
    dr, tickers, covMatrix = op.processData()
    expAR = op.expectedAnnualReturns(dr)
    # if we set low risk we should expect that coef of E should be less than the rest and A and C which have zero risk should have larger coef.
    op.risk = 0.01
    res = op.maximizePortfolioReturns(covMatrix, tickers, expAR).round(4)
    print(res)
    assert res[0] > res[1]
    assert res[0] > res[4]
    assert res[0] > res[3]
    assert res[2] > res[1]
    assert res[2] > res[4]
    assert res[2] > res[3]
    # set high risk then coef of A and C should be smaller and coed of E should be larger
    op.risk = 0.99
    res = op.maximizePortfolioReturns(covMatrix, tickers, expAR).round(4)
    print(res)
    assert res[0] < res[1]
    assert res[0] < res[4]
    assert res[0] < res[3]
    assert res[2] < res[1]
    assert res[2] < res[4]
    assert res[2] < res[3]


def test_plot():
    import matplotlib.pyplot as plt

    closeValuesLR = {
        "A": [1, 1, 1, 1, 1],  # zero risk zero return
        "B": [1000, 1200, 960, 1152, 921.6],  # risk = 0.053333, return 0
        "C": [100, 100, 100, 100, 100],  # zero risk zero return
        "D": [100, 101, 102, 101, 102],  # low risk  return 1.259878
        "E": [20, 23, 24, 18, 40],  # hight risk high return
        "Date": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 2),
            datetime(2022, 1, 3),
            datetime(2022, 1, 4),
            datetime(2022, 1, 5),
        ],
    }
    dataLR = pd.DataFrame(closeValuesLR)
    op = OptimisePortfolio(
        dataLR,
        1,
        risk=0,
        useLogReturns=False,
        workDaysinYear=252,
        objectFunction="Sharpe",
    )
    dr, tickers, covMatrix = op.processData()
    expAR = op.expectedAnnualReturns(dr)
    result_df = op.genRandomPortfolios(
        expReturnsAnnual=expAR, covMatrix=covMatrix, tickers=tickers, n_iter=10000
    )
    print(result_df[["risk", "returns"]].head(), result_df.columns)
    plt.scatter(result_df.risk, result_df.returns)
    for risk in np.arange(0.0, 5, 0.1):
        op.risk = risk
        weights = op.maximizePortfolioReturns(covMatrix, tickers, expAR).round(4)
        portfolioReturn = op.portfolioReturns(weights=weights, expReturnsAnnual=expAR)
        portRisk = op.portfolioRisk(weights=weights, covMatrix=covMatrix)
        plt.scatter(portRisk, portfolioReturn, color="red")
    plt.show()
