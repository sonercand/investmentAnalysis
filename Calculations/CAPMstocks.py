import numpy as np
import pandas as pd
import yfinance as yf


class CAPM:
    def __init__(self, stocks, start_date, end_date):
        stocks = set(stocks)
        self.stocks = list(stocks)
        self.start_date = start_date
        self.end_date = end_date
        self.UKMarketTicker = "^FTMC"
        self.USMarketTIcker = "^GSPC"
        self.data = self.downloadData()
        self.data.columns = self.columns
        self.splitUKUS()
        self.setMarketData()

    def splitUKUS(self):
        self.ukStocks = [stock for stock in self.stocks if stock.upper().endswith(".L")]
        self.usStocks = [
            stock for stock in self.stocks if not stock.upper().endswith(".L")
        ]

    def setMarketData(self):
        usm = yf.download(self.USMarketTIcker, self.start_date, self.end_date)[
            "Adj Close"
        ]
        self.usMarket = (usm).resample("M").last()
        uk = yf.download(self.UKMarketTicker, self.start_date, self.end_date)[
            "Adj Close"
        ]
        self.ukMarket = (uk).resample("M").last()

    def downloadData(self):
        data_ = []
        j = 0
        self.columns = []
        for stock in self.stocks:
            try:
                dfT = yf.download(stock, self.start_date, self.end_date)["Adj Close"]
                if len(dfT) > 5:
                    data_.append(dfT)
                    self.columns.append(stock)
                else:
                    print("data frame has few rows")
                    print(dfT)
                    print(stock)
            except Exception as e:
                print(e)
                print(stock)
                self.stocks.remove(stock)

        df = pd.concat(data_, axis=1)
        return df.resample("M").last()

    def logReturns(self, data):
        return (np.log(data / data.shift(1)))[1:]

    def getRiskFreeRate(self):
        """using 13 week treasure bill ^IRX"""
        return yf.download("^IRX", self.start_date, self.end_date)["Adj Close"][-1]

    def Beta(self, ticker):
        if ticker in self.ukStocks:
            covMatrix = np.cov(
                self.logReturns(self.data[ticker]), self.logReturns(self.ukMarket)
            )
        elif ticker in self.usStocks:
            covMatrix = np.cov(
                self.logReturns(self.data[ticker]), self.logReturns(self.usMarket)
            )
        else:
            return "Ticker not found"
        return (
            covMatrix[0, 1] / covMatrix[1, 1]
        )  # note diagonals are the variance in the np cov matrix

    def expectedReturnMarket(self, ticker):
        if ticker in self.ukStocks:
            return self.logReturns(self.ukMarket).mean()
        if ticker in self.usStocks:
            return self.logReturns(self.usMarket).mean()

    def expectedReturnMonthly(self, ticker, numMonths=1):
        riskFreeRate = self.getRiskFreeRate() / 100
        return riskFreeRate + self.Beta(ticker) * (
            self.expectedReturnMarket(ticker) * numMonths - riskFreeRate
        )

    def run(self):
        expectedReturns = []
        for stock in self.stocks:
            try:
                expectedReturns.append(
                    {
                        "ticker": stock,
                        "expectedReturn": self.expectedReturnMonthly(stock, 12),
                    }
                )
            except Exception as e:
                print(stock)
        return pd.DataFrame(expectedReturns)


if __name__ == "__main__":
    from datetime import datetime, date
    from dateutil.relativedelta import relativedelta

    today = date.today()
    twoYearAgo = today - relativedelta(years=2)
    today = today.strftime("%Y-%m-%d")
    twoYearAgo = twoYearAgo.strftime("%Y-%m-%d")
    print(today, twoYearAgo)
    stocks = list(pd.read_csv("./data/snpFtseClose.csv").columns)

    try:
        stocks.remove("Date")
    except:
        stocks.remove("Unnamed: 0")
    print(len(stocks))
    # stocks = ["mng.l", "AAPL", "MSFT", "PRU.L"]
    capm = CAPM(stocks=stocks, start_date=twoYearAgo, end_date=today)
    retDf = capm.run()
    retDf.to_csv("./data/expectedReturns4monthlyCAPM.csv", index=False)
