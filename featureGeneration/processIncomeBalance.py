from cmath import nan
import pandas as pd
import numpy as np

bs_ = pd.read_csv("./data/balance_sheetSNP.csv")

"""
# order and clean balance sheet #############
bs_.replace("None", nan, inplace=True)  # replace string None with nan
bs_["fiscalDateEnding"] = pd.to_datetime(bs_.fiscalDateEnding)  # convert to datetime
bs_ = bs_.sort_values(by=["fiscalDateEnding"])  # order by datetime


bs_columns = list(bs_.columns)
bs_columns.remove("fiscalDateEnding")
bs_columns.remove("reportedCurrency")
bs_columns.remove("ticker")
print(len(bs_columns))
for col in bs_columns:
    if 100 * len(bs_[bs_[col].isnull()]) / len(bs_) > 30:
        bs_columns.remove(col)
print(len(bs_columns))
print(bs_columns)

# get pct change and save data
tickers = bs_.ticker.unique()
bs_array = []
for ticker in tickers:
    bs_sub = bs_[bs_.ticker == ticker].copy()

    bs_features = bs_sub[bs_columns]
    bs_features = bs_features.astype(np.float)
    bs_sub = bs_sub[["ticker", "fiscalDateEnding"]]

    bs_sub[bs_columns] = bs_features.pct_change(1)
    bs_array.append(bs_sub)
bs_df = pd.concat(bs_array)
bs_df.to_csv("./data/balanceFeatures.csv", index=False)
"""
is_ = pd.read_csv("./data/income_statementsSNP.csv")
print(is_)
# order and clean balance sheet #############
is_.replace("None", nan, inplace=True)  # replace string None with nan
is_["fiscalDateEnding"] = pd.to_datetime(is_.fiscalDateEnding)  # convert to datetime
is_ = is_.sort_values(by=["fiscalDateEnding"])  # order by datetime


is_columns = list(is_.columns)
is_columns.remove("fiscalDateEnding")
is_columns.remove("reportedCurrency")
is_columns.remove("ticker")
print(len(is_columns))
for col in is_columns:
    if 100 * len(is_[is_[col].isnull()]) / len(is_) > 30:
        is_columns.remove(col)
print(len(is_columns))
print(is_columns)


tickers = is_.ticker.unique()
is_array = []
for ticker in tickers:
    is_sub = is_[is_.ticker == ticker].copy()

    is_features = is_sub[is_columns]
    is_features = is_features.astype(np.float)
    is_sub = is_sub[["ticker", "fiscalDateEnding"]]

    is_sub[is_columns] = is_features.pct_change(1)
    is_array.append(is_sub)
is_df = pd.concat(is_array)
is_df.to_csv("./data/incomeFeatures.csv", index=False)
