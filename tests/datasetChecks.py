import pandas as pd

df = pd.read_csv("./data/balance_sheetSNP.csv")
print(df.head())
print(len(df.ticker.unique()))

print(df.fiscalDateEnding.unique())
print(df.fiscalDateEnding.max(), df.fiscalDateEnding.min())
print(df.columns)
print("------------")
df = pd.read_csv("./data/income_statementsSNP.csv")
print(df.head())
