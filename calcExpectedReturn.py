from time import time
from black import main
import pandas_datareader.data as web
from datetime import datetime, timedelta

tic = "TSLA"
end = datetime.today()
days = timedelta(365)
start = end - days

print(end, start)

df = web.DataReader(tic, "yahoo", start=start, end=end)


def getExpectedReturn(dataFrame, priceColumn):
    """calculate annual expected return as a percentage"""
    returns = dataFrame[priceColumn].pct_change(1)
    meanExpectedReturnDaily = returns.mean()
    eReturn = ((1 + meanExpectedReturnDaily) ** 250) - 1
    return eReturn * 100


if __name__ == "__main__":
    ret = getExpectedReturn(df, "Close")
    print(ret)
