import yfinance as yf
import numpy as np
import pandas as pd


def getData(tickers, period):
    data = yf.Tickers(tickers)
    return data.history(period=period)["Close"]


def getDailyReturns(dataFrame):
    dr = dataFrame.pct_change(1)
    dr.dropna(inplace=True)
    return dr


def calcWeights(weightsRaw):
    if np.sum(weightsRaw) != 1:
        return weightsRaw / np.sum(weightsRaw)
    else:
        return weightsRaw


def expectedPortfolioReturn(dataFrame, weightsRaw):
    weights = calcWeights(weightsRaw)
    dr = getDailyReturns(dataFrame)
    avg_daily_returns = np.mean(dr, axis=0)
    exceptedAnnualisedReturns = ((1 + avg_daily_returns) ** 250) - 1
    return np.dot(weights, exceptedAnnualisedReturns)


def portfolioSTD(dailyReturns, weigths):
    weigths = calcWeights(weigths)
    covMatrix = dailyReturns.cov()
    varPort = np.dot(np.transpose(weigths), np.dot(covMatrix, weigths))
    stdPort = np.sqrt(varPort)
    stdPortAnnual = stdPort * np.sqrt(250)
    indStockAnnualStd = np.std(dailyReturns) * np.sqrt(250)
    return stdPortAnnual, indStockAnnualStd
