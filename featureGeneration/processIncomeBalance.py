import pandas as pd

bs_ = pd.read_csv("./data/balance_sheetSNP.csv")
is_ = pd.read_csv("./data/income_statementsSNP.csv")

# get pct change
bs_pct = bs_.pct_change(1)
print(bs_pct.head())
