import yfinance as yf
from portfolioAnalytics import getData
import pandas as pd

fComp = pd.read_csv("./data/ftse100components.csv")
sComp = pd.read_csv("./data/snp500components.csv")

tickers = []
tickers = list(fComp["symbol"]) + list(sComp["Symbol"])
print(len(tickers))

period = "5y"
data = getData(tickers, period)
data.to_csv("./data/snpFtseClose.csv", index=False)
print(data.head())
