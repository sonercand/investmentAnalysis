from turtle import st
from Calculations.portfolioOptimisation import OptimisePortfolio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

global stocks
stocks = ["A", "B", "C"]
global closeValues
closeValues = {
    "A": [100, 100, 100, 100],
    "B": [100, 110, 220, 220 * 4],
    "C": [1, 2, 4, 8],
    "date": [
        datetime(2022, 1, 1),
        datetime(2022, 1, 2),
        datetime(2022, 1, 3),
        datetime(2022, 1, 4),
    ],
}
global data
data = pd.DataFrame(closeValues)
global op
op = OptimisePortfolio(
    data,
    1,
    risk=[0.2],
    useLogReturns=True,
    workDaysinYear=252,
    objectFunction="Sharpe",
)


def test_init():
    pd.testing.assert_frame_equal(op.data, data)
    assert op.useRiskRange == True


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
    returnsPct = op.calculateReturn(data[stocks]).round(3)
    expectedReturns = [[0.0, 0.1, 1.0], [0.0, 1.0, 1.0], [0.0, 3.0, 1.0]]
    for e, a in zip(returnsPct.values, expectedReturns):
        assert list(e) == list(a)


if __name__ == "__main__":
    test_calculateReturn()
