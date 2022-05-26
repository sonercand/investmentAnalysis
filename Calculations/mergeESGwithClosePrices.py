import pandas as pd
import yfinance as yf

dfClose = pd.read_csv("./data/snpFtseClose.csv")
dfESG = pd.read_csv("./data/esgScores.csv")
print("dfESG")
print(dfESG)
print(dfClose.head())
print(dfESG.head())
dfc = dfClose.head(1)
new_df = dfc.copy(deep=True)
new_df1 = pd.DataFrame()
for col in dfc.columns:
    if col != "Date":
        print((dfESG[dfESG.ticker == col].numericRate.values))
        new_df1[col] = dfESG[dfESG.ticker == col].numericRate.values
print("new_df")
print(new_df1)
new_df1.to_csv("./data/esgScores_aligned.csv", index=False)
