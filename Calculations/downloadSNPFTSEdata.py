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
df.to_csv("./data/sectors.csv", index=False)
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
media = []
hospitality = []
chemicals = []
queue = list(sectors).copy()

while True:
    sec = queue.pop(0)
    if "media" in sec.lower():
        media.append(sec)
    if (
        "financial" in sec.lower()
        or "finance" in sec.lower()
        or "insurance" in sec.lower()
        or "bank" in sec.lower()
        or "investment" in sec.lower()
        or "asset" in sec.lower()
        or "trad" in sec.lower()
    ):
        financial_services.append(sec)
    if "telecom" in sec.lower() or "communication" in sec.lower():
        telecomunication.append(sec)
    if "tobacco" in sec.lower():
        tobacco.append(sec)
    if "oil" in sec.lower() or "gas" in sec.lower() or "energy" in sec.lower():
        oil_and_gas.append(sec)
    if "defence" in sec.lower():
        defence_military.append(sec)
    if "casino" in sec.lower() or "gambling" in sec.lower():
        gambling_casino.append(sec)
    if "mining" in sec.lower() or "gold" in sec.lower() or "copper" in sec.lower():
        mining.append(sec)
    if (
        "pharma" in sec.lower()
        or "drug" in sec.lower()
        or "health" in sec.lower()
        or "medic" in sec.lower()
        or "biotec" in sec.lower()
    ):
        health_and_pharma.append(sec)
    if "restaurant" in sec.lower() or "hotel" in sec.lower() or "travel" in sec.lower():
        hospitality.append(sec)
    if "chemistry" in sec.lower() or "chemical" in sec.lower():
        chemicals.append(sec)
    if len(queue) == 0:
        break
rest = list(set(sectors) - set(health_and_pharma))
rest = set(rest) - set(mining)
rest -= set(gambling_casino)
rest -= set(defence_military)
rest -= set(oil_and_gas)
rest -= set(tobacco)
rest -= set(telecomunication)
rest -= set(financial_services)
rest -= set(media)
rest -= set(hospitality)
rest -= set(chemicals)
rest = list(rest)
sector_dict = {
    "Healthcare, Pharma and Biotech": health_and_pharma,
    "Mining": mining,
    "Gambling": gambling_casino,
    "Arms and Defence": defence_military,
    "Oil and Gas": oil_and_gas,
    "Tobacco": tobacco,
    "Telecom": telecomunication,
    "Financial Services": financial_services,
    "Media": media,
    "Hospitality": hospitality,
    "Chemicals": chemicals,
    "rest": rest,
}
period = "5y"
data = getData(tickers, period)
data.to_csv("./data/snpFtseClose.csv", index=True)


sectors_stock = {}
for key, value in sector_dict.items():
    sectors_stock[key] = list(df[df.sector.isin(value)].symbol.values)

import json

with open("./data/sector_map.json", "w") as fp:
    json.dump(sectors_stock, fp)
