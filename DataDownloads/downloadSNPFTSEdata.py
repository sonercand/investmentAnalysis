from tokenize import Ignore
import yfinance as yf
from Calculations.portfolioAnalytics import getData
import pandas as pd

fComp = pd.read_csv("./data/ftse100components.csv")
sComp = pd.read_csv("./data/snp500components.csv")

tickers = []
tickers = list(fComp["symbol"]) + list(sComp["Symbol"])


# data = getData(tickers, period="5y")
# data.to_csv("./data/snpFtseClose.csv", index=True)

# save adj close data for the tickers

dfs = []
for ticker in tickers:
    new_df = pd.DataFrame()
    try:
        data = yf.download(ticker, "2017-05-26", "2022-05-25")
        data = data["Adj Close"]
        new_df[ticker] = data

        dfs.append(new_df)
    except Exception as e:
        print(e)
        print(ticker)
new_df = pd.concat(dfs, axis=1)

new_df.to_csv("./data/snpFtseClose.csv", index=True)
