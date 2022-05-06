from time import time
from black import main
import pandas_datareader.data as web
from datetime import datetime, timedelta

tic = "TSLA"
end = datetime.today()
days = timedelta(365)
start = end - days


df = web.DataReader(tic, "yahoo", start=start, end=end)


def getExpectedReturn(dataFrame, priceColumn):
    """calculate annual expected return as percent"""
    returns = dataFrame[priceColumn].pct_change(1)
    returns.dropna(inplace=True)
    print(len(returns))
    meanExpectedReturnDaily = returns.mean()
    eReturn = ((1 + meanExpectedReturnDaily) ** len(returns)) - 1
    return eReturn


if __name__ == "__main__":
    ret = getExpectedReturn(df, "Close")
    print(ret)
