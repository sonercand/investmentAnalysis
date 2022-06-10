import os
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

fs = os.listdir("./data/modeldata")

# load data sets and filter for snp500 stocks
adjC = pd.read_csv("./data/snpFtseClose.csv")
cols = list(adjC.columns)
cols = [
    col for col in cols if not col.upper().endswith(".L")
]  # remove LSE stocks tickers
adjC = adjC[cols]
adjC["Date"] = pd.to_datetime(adjC.Date)
adjC = adjC.sort_values(by=["Date"])
adjC.ffill(inplace=True)
adjC.bfill(inplace=True)
stocks = list(cols).copy()
stocks.remove("Date")
bsF = pd.read_csv("./data/balanceFeatures.csv")
bsF["fiscalDateEnding"] = pd.to_datetime(bsF["fiscalDateEnding"])
# load income statement
isF = pd.read_csv("./data/incomeFeatures.csv")
# load momentum
momentum = pd.read_csv("./data/momentumSNP.csv")

for stock in [stocks[1]]:
    try:
        # checks##########
        # 1) stock price data
        yLabel = adjC[[stock, "Date"]]

        # 2) balance sheet data
        bsF_sub = bsF[bsF.ticker == stock]  # filter balance sheet for the given stock

        xBase = adjC[["Date", stock]]  # create a base df
        xBase["rollingMean"] = (
            xBase[[stock]].rolling(int(252.0 / 4.0)).mean()
        )  # 63 days rolling average
        # join balance sheet ###################################
        query = """
        with get_data as (
        select t1.*,t2.* from xBase t1 left join bsF_sub t2 on t2.fiscalDateEnding<=t1.Date) 
        select distinct gd.* from get_data gd inner join(select Date, max(fiscalDateEnding) as max_ from get_data group by Date) t3 on
        t3.Date = gd.Date and t3.max_ =gd.fiscalDateEnding
        """
        pysqldf = lambda q: sqldf(q, globals())
        dfm = pysqldf(query)
        dfm["fiscalDateEnding2"] = dfm["fiscalDateEnding"]
        dfm.drop(["fiscalDateEnding"], axis=1, inplace=True)
        # drop null columns
        dfm = dfm.dropna(axis=1, how="all")
        isF_sub = isF[isF.ticker == stock]
        isF_sub["fiscalDateEnding"] = pd.to_datetime(isF_sub["fiscalDateEnding"])
        query = """
        with get_data as (
            select t1.*,t2.* from dfm t1 left join isF_sub t2 on t2.fiscalDateEnding<=t1.Date
        )select distinct gd.* from get_data gd inner join(select Date, max(fiscalDateEnding) as max_ from get_data group by Date) t3 on
        t3.Date = gd.Date and t3.max_ =gd.fiscalDateEnding
        """
        dfa = pysqldf(query)
        dfa = dfa.dropna(axis=1, how="all")
        # join rolling momentum #######################
        moment = momentum[["Date", stock]]
        moment["Date"] = pd.to_datetime(moment["Date"])
        query = """
            select t1.*,t2.`{}` as momentum from dfa t1 left  join moment t2 on t1.Date== t2.Date
        """.format(
            stock
        )
        dff = pysqldf(query)
        dff = dff.dropna(axis=1, how="all")
        # process data to add labels
        dff["Date"] = pd.to_datetime(dff.Date)

        infomationColumns = set(
            [
                "Date",
                stock,
                "ticker",
                "fiscalDateEnding",
                "fiscalDateEnding2",
                "ticker:1",
            ]
        )
        dffL = dff
        predictionPoint = dffL.iloc[-1:]  # take the last data point for the prediction

        columns = set(dffL.columns)
        features_cols = columns - infomationColumns
        features_cols = list(features_cols)

        dffL = dffL[~dffL.isin([np.inf, -np.inf]).any(1)]
        predictionPoint = predictionPoint[
            ~predictionPoint.isin([np.inf, -np.inf]).any(1)
        ]
        predictionPoint = predictionPoint.fillna(0)
        dffL = dffL.fillna(0)

        features_and_labels = dffL[features_cols]
        print(features_and_labels.shape, predictionPoint[features_cols].shape)
        try:
            scaler = MinMaxScaler()
            scaler.fit(features_and_labels)
            scaled = scaler.transform(features_and_labels)
        except Exception as e:
            print(e)
            print(stock)
            print("dffL")
            print(dffL)
            print("dff")
            print(dff)
        print(scaled.shape)
        predictionPoint_m = predictionPoint.fillna(0)
        print("prediction pont")
        predictionPoint_m = predictionPoint_m[features_cols]
        print(predictionPoint_m.values)
        predictionPoint_m = scaler.fit_transform(
            predictionPoint_m.values.reshape(-1, 1)
        )

        bst_model_path = "./data/modeldata/{}.h5".format(stock)

        model = keras.Sequential(
            [
                layers.Dense(64, activation="relu"),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                layers.Dense(32, activation="relu"),
                layers.BatchNormalization(),
                layers.Dense(1),
            ]
        )
        model.build(predictionPoint_m)
        model.compile(
            loss="mean_absolute_percentage_error",
            optimizer=tf.keras.optimizers.Adam(0.01),
        )

        model.load_weights(bst_model_path)
        test_r = {}

        test_prediction = model.predict(predictionPoint_m).flatten()

    except Exception as e:
        print(e)
