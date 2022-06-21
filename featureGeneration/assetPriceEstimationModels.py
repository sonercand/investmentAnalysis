"""
# Estimate expected asset price using ml
* features are: balance sheets, income balance for the last 5 years and momentum
* scope: portfolio will be reallocated every 13 weeks therefore every 13 weeks returns should be estimated for the next reallocation date.



"""
from pyexpat import features
from this import d
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
print(momentum)
### CREATE A MODEL PER STOCK ####################################
for stock in stocks[1:2]:
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

        dff["labelDate"] = dff["Date"] + timedelta(days=int(252 / 4))
        if stock == "ALL":  # ALL is giving sql error as a column
            dff["nALL"] = dff["ALL"]
            dff.drop("ALL", axis=1, inplace=True)
            stock = "nALL"
        query = """
        with get_data as ( select * from dff)
        select gd.*,t2.col as label from get_data gd left join (select  Date,{} as col from get_data) t2 on gd.labelDate=t2.Date
        """.format(
            stock
        )

        dffL = pysqldf(query)
        dffL = dffL.dropna(axis=1, how="all")
        predicionPoint = dffL.iloc[-1:]

        if stock == "nALL":
            dffL["ALL"] = dffL["nALL"]
            dffL.drop("nALL", axis=1, inplace=True)
            stock = "ALL"
        # dffL.dropna(inplace=True)  # drop na

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
        predictionPoint = predicionPoint[~predicionPoint.isin([np.inf, -np.inf]).any(1)]
        predictionPoint.replace([np.inf, -np.inf], np.nan, inplace=True)
        predictionPoint = predicionPoint.fillna(0)

        features_and_labels = dffL[features_cols]
        predictionPoint = predictionPoint[features_cols]
        cols = list(features_and_labels.columns)
        cols.remove("label")
        features_and_labels = features_and_labels[cols]
        predictionPoint = predictionPoint[cols]
        label = dffL[label_col]
        # scaling:
        try:
            scaler = MinMaxScaler()
            scaler.fit(features_and_labels)
            scaled = scaler.transform(features_and_labels)
            print(predictionPoint.shape)
            print(scaled.shape)
            print("scaling prediction point")
            scaledPredictionPoint = scaler.transform(predictionPoint)
            print(scaledPredictionPoint.shape)

        except Exception as e:
            print(e)
            print(stock)
            print("dffL")
            print(dffL)
            print("dff")
            print(dff)

        featuresTrain, featuresVal, labelsTrain, labelsVal = train_test_split(
            features_and_labels, label, test_size=0.15, random_state=12
        )

        bst_model_path = "./data/modeldata/{}.h5".format(stock)
        model_checkpoint = ModelCheckpoint(
            bst_model_path, save_best_only=True, save_weights_only=True
        )

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
        model.build(featuresTrain.shape)
        model.compile(
            loss="mean_absolute_percentage_error",
            optimizer=tf.keras.optimizers.Adam(0.01),
        )
        history = model.fit(
            featuresTrain,
            labelsTrain,
            epochs=150,
            # Suppress logging.
            verbose=0,
            validation_split=0.1,
            callbacks=[model_checkpoint],
        )
        model.load_weights(bst_model_path)
        test_r = {}
        test_r[stock] = model.evaluate(featuresVal, labelsVal, verbose=0)
        print(test_r)
        test_predictions = model.predict(featuresVal).flatten()
        predictionPointPred = model.predict(scaledPredictionPoint)
        print(predictionPoint)
        print(predictionPointPred[0])
    except Exception as e:
        print(e)
        print(stock)
