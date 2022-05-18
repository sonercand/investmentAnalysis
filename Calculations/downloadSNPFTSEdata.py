from tokenize import Ignore
import yfinance as yf
from portfolioAnalytics import getData
import pandas as pd

fComp = pd.read_csv("./data/ftse100components.csv")
sComp = pd.read_csv("./data/snp500components.csv")

tickers = []
tickers = list(fComp["symbol"]) + list(sComp["Symbol"])

sectorsF = fComp[["sector", "symbol"]]

sectorsS = sComp[["GICS Sub-Industry", "Symbol"]]

sectorsS.columns = ["sector", "symbol"]
df = pd.concat([sectorsF, sectorsS], ignore_index=True)
# df.to_csv("./data/sectors.csv", index=False)
sectors = df.sector.unique()
financial_services = []
telecomunication = []
tobacco = []
oil_and_gas = []
mining = []
rest = []
defence_military = []
gambling_casino = []
health_and_pharma = []
queue = list(sectors).copy()

while True:
    sec = queue.pop(0)
    if (
        "financial" in sec.lower()
        or "insurance" in sec.lower()
        or "bank" in sec.lower()
        or "investment" in sec.lower()
        or "asset" in sec.lower()
    ):
        financial_services.append(sec)
    if "telecom" in sec.lower():
        telecomunication.append(sec)
    if "tobacco" in sec.lower():
        tobacco.append(sec)
    if "oil" in sec.lower() or "gas" in sec.lower():
        oil_and_gas.append(sec)
    if "defence" in sec.lower():
        defence_military.append(sec)
    if "casino" in sec.lower() or "gambling" in sec.lower():
        gambling_casino.append(sec)
    if "mining" in sec.lower():
        mining.append(sec)
    if (
        "pharma" in sec.lower()
        or "drug" in sec.lower()
        or "health" in sec.lower()
        or "medic" in sec.lower()
        or "biotec" in sec.lower()
    ):
        health_and_pharma.append(sec)

    if len(queue) == 0:
        break

health_and_pharma_stocks = df[df.sector.isin(health_and_pharma)]
exclusion_stocks = {}
exclusion_stocks["Healthcare and Pharma"] = list(health_and_pharma_stocks.symbol.values)
exclusion_stocks["Mining"] = list(df[df.sector.isin(mining)].symbol.values)
exclusion_stocks["Gambling"] = list(df[df.sector.isin(gambling_casino)].symbol.values)
exclusion_stocks["Arms and Defence"] = list(
    df[df.sector.isin(defence_military)].symbol.values
)
exclusion_stocks["Oil and Gas"] = list(df[df.sector.isin(oil_and_gas)].symbol.values)
exclusion_stocks["Tobacco"] = list(df[df.sector.isin(tobacco)].symbol.values)
exclusion_stocks["Telecom"] = list(df[df.sector.isin(telecomunication)].symbol.values)
exclusion_stocks["Financial Services"] = list(
    df[df.sector.isin(financial_services)].symbol.values
)
df2 = pd.DataFrame.from_dict(exclusion_stocks, orient="index")
df2.to_csv("./data/exclusion_stocks.csv")


period = "5y"
data = getData(tickers, period)
data.to_csv("./data/snpFtseClose.csv", index=False)
