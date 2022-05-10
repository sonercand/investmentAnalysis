import numpy as np
import yfinance as yf


def calculateVolatility(tic):
    data = yf.Ticker(tic)
    hist = data.history(period="1y")
    hist["returns"] = hist["Close"].pct_change(1)
    std = np.std(hist["returns"], ddof=1)
    mean = np.mean(hist["returns"])
    hist["returns_norm"] = (hist["returns"] - mean) / std
    vol = std * np.sqrt(len(hist["returns_norm"]))
    return vol, hist[["returns_norm"]]
