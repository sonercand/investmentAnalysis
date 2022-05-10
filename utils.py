import yfinance as yf
import finnhub as fh
import os
import pandas as pd
from dotenv import load_dotenv


def getExchanges():
    df = pd.read_csv("./data/exchanges.csv")
    arr = df[["code", "name"]].values
    dict_ = {}
    for code, name in arr:
        dict_[name] = code
    return dict_


class StockMarketInformation:
    def __init__(self, sandbox=False, tic=None):
        self.sandbox = sandbox
        load_dotenv()
        if self.sandbox:
            api_key = os.getenv("FINHUB_API_KEY_SANDBOX")
        else:
            api_key = os.getenv("FINHUB_API_KEY")
        self.finnhub_client = fh.Client(api_key=api_key)
        if tic != None:
            self.setTic(tic)
            self.setYFData(tic)

    def setTic(self, tic):
        self.tic = tic

    def setYFData(self, tic=None):
        tic = tic if tic != None else self.tic
        data = yf.Ticker(tic)
        self.yData = data

    def getCompanyInfo(self, tic=None):
        """
        args:
            tic : string : equity ticker
        return:  a dictionary with the fields:
            country, exchange, finhubIndustry, ipo, logo, marketCapitalisation, name,phone,shareOutstanding, ticker, weburl
        """
        tic = tic if tic != None else self.tic
        return self.finnhub_client.company_profile2(symbol=tic)

    def getStockSymbols(self, exchange):
        """
        args:
            exchange: str : exchange symbol
        returns:
            list of stock tics
        """
        return self.finnhub_client.stock_symbols(exchange)

    def getStockSymbolList(self, list_):
        return [item["symbol"] for item in list_]

    def getHistoricalData(self, period, tic=None):
        """
        args:
            tick
            period: string:  valid periods are 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        """
        tic = tic if tic != None else self.tic
        data = yf.Ticker(tic)
        hist = data.history(period=period)
        return hist

    def getESGData(self, tic):
        data = yf.Ticker(tic)
        return data.sustainability

    def getTotalESGScore(self, tic=None):
        esgData = self.getESGData(tic)
        return esgData.totalEsg.values[0]
