from bs4 import BeautifulSoup
from numpy import save
import requests
import pandas as pd


def saveFSTE100Components():
    page = requests.get("https://en.wikipedia.org/wiki/FTSE_100_Index")
    soup = BeautifulSoup(page.content, "html.parser")
    idTable = "constituents"
    table = soup.find("table", id=idTable)

    headers = [header.text for header in table.find_all("th")]
    rows = [val for val in table.find_all("tr")]
    symbols = []
    ftse100 = []
    for row in rows:
        rowVals = [val.string for val in row.find_all("td")]
        if len(rowVals) > 0:
            industry = rowVals[2]
            industry = industry.replace("\n", "")
            ftse100.append({"symbol": rowVals[1] + ".L", "sector": rowVals[2]})
    df = pd.DataFrame(ftse100)
    print(df.head())
    df.to_csv("./data/ftse100Components.csv", index=False)


if __name__ == "__main__":
    saveFSTE100Components()
    print(pd.read_csv("./data/ftse100Components.csv"))
