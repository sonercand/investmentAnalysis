"""
# Estimate expected asset price using ml
* features are: balance sheets, income balance for the last 5 years and momentum
* scope: portfolio will be reallocated every 13 weeks therefore every 13 weeks returns should be estimated for the next reallocation date.



"""

import pandas as pd
from pandasql import sqldf
from datetime import timedelta
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None  # default='warn'
# Load Current Adjusted close prices(5 years)
adjC = pd.read_csv("./data/snpFtseClose.csv")
##################################### DATA PROCESSING ##############################################
# 1) filter for snp500
adjC["Date"] = adjC["Unnamed: 0"]
adjC.drop(["Unnamed: 0"], axis=1, inplace=True)
cols = list(adjC.columns)
cols = [
    col for col in cols if not col.upper().endswith(".L")
]  # remove LSE stocks tickers
adjC = adjC[cols]
# 2) replace nan

adjC["Date"] = pd.to_datetime(adjC.Date)
adjC = adjC.sort_values(by=["Date"])
adjC.ffill(inplace=True)
adjC.bfill(inplace=True)
stocks = list(cols).copy()
stocks.remove("Date")
# load Balance Sheet and Income Statements
bsF = pd.read_csv("./data/balanceFeatures.csv")
bsF["fiscalDateEnding"] = pd.to_datetime(bsF["fiscalDateEnding"])
# load income statement
isF = pd.read_csv("./data/incomeFeatures.csv")
# load momentum
momentum = pd.read_csv("./data/momentumSNP.csv")

### CREATE A  Generic Momentum Model ####################################
processedFrames = []
for stock in stocks:
    try:
        # add rolling means
        xBase = adjC[["Date", stock]]  # create a base df
        xBase["rollingMean2m"] = xBase[[stock]].rolling(int(252.0 / 6.0)).mean()
        xBase["rollingMean4m"] = xBase[[stock]].rolling(int(252.0 / 4.0)).mean()
        xBase["rollingMean6m"] = xBase[[stock]].rolling(int(252.0 / 2.0)).mean()
        xBase = xBase.iloc[int(252.0 / 2.0) :]  #
        # add momentum
        moment = momentum[["Date", stock]]
        moment["Date"] = pd.to_datetime(moment["Date"])
        query = """
                select t1.*,t2.`{}` as momentum from xBase t1 left  join moment t2 on t1.Date== t2.Date
            """.format(
            stock
        )
        pysqldf = lambda q: sqldf(q, globals())
        dff = pysqldf(query)
        print(xBase.shape, dff.shape, moment.shape)
        # process data to add labels
        dff["Date"] = pd.to_datetime(dff.Date)
        dff["labelDate"] = dff["Date"] + timedelta(days=int(252 / 4))
        if stock == "ALL":  # ALL is giving sql error as a column
            dff["nALL"] = dff["ALL"]
            dff.drop("ALL", axis=1, inplace=True)
            stock = "nALL"
        query = """
            with get_data as ( select * from dff)
            select gd.*,(t2.col-gd.{})/gd.{} as label from get_data gd left join (select  Date,{} as col from get_data) t2 on gd.labelDate=t2.Date
            """.format(
            stock, stock, stock
        )

        dffL = pysqldf(query)
        print(dffL.head())
        if stock == "nALL":
            dffL["ALL"] = dffL["nALL"]
            dffL.drop("nALL", axis=1, inplace=True)
            stock = "ALL"
        infomationColumns = set(
            [
                "Date",
                stock,
                "ticker",
                "fiscalDateEnding",
                "fiscalDateEnding2",
                "labelDate",
                "ticker:1",
            ]
        )
        columns = set(dffL.columns)
        features_cols = columns - infomationColumns
        features_cols = list(features_cols)
        label_col = "label"
        dffL.replace([np.inf, -np.inf], np.nan, inplace=True)
        dffL = dffL.dropna(subset=["label"])
        dffL = dffL.fillna(0)

        features_and_labels = dffL[features_cols]
        processedFrames.append(features_and_labels)
    except Exception as e:
        print(e)
        print(stock)
        continue

processed = pd.concat(processedFrames)
processed.to_csv("./data/modeldata/processedMomentumModelData.csv", index=False)
print(processed.shape)
print(processed)
