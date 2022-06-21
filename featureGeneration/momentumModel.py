import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from keras.callbacks import ModelCheckpoint
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_error
from pandasql import sqldf
from datetime import timedelta

data = pd.read_csv("./data/modeldata/processedMomentumModelData.csv")
features = data[["rollingMean4m", "rollingMean2m", "rollingMean6m", "momentum"]]
# scale dataset
# features = (features - features.min()) / (features.max() - features.min())
label = data["label"]
# print(data.columns)
featuresTrain, featuresVal, labelsTrain, labelsVal = train_test_split(
    features.values, label.values, test_size=0.15, random_state=12
)

params = {
    "task": "train",
    "boosting": "gbdt",
    "objective": "regression",
    "num_leaves": 10,
    "learnnig_rage": 0.01,
    "num_iterations": 500,
    "metric": {"l2", "l1"},
    "verbose": -1,
}
lgb_train = lgb.Dataset(featuresTrain, labelsTrain)
lgb_eval = lgb.Dataset(featuresVal, labelsVal, reference=lgb_train)
model = lgb.train(
    params, train_set=lgb_train, valid_sets=lgb_eval, early_stopping_rounds=30
)

y_pred = model.predict(featuresVal)
# print(np.max(y_pred), np.min(y_pred))
# print(y_pred)
# accuracy check
mse = mean_squared_error(labelsVal, y_pred)
mae = mean_absolute_error(labelsVal, y_pred)
rmse = mse ** (0.5)
# print("MSE: %.2f" % mse)
# print("RMSE: %.2f" % rmse)
# print("MAE: %.2f" % mae)


## Calculate Predictions#############################
adjC = pd.read_csv("./data/snpFtseClose.csv")
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
momentum = pd.read_csv("./data/momentumSNP.csv")
predictions = []
for stock in stocks:
    try:
        # add rolling means
        xBase = adjC[["Date", stock]]  # create a base df
        xBase["rollingMean2m"] = xBase[[stock]].rolling(int(252.0 / 6.0)).mean()
        xBase["rollingMean4m"] = xBase[[stock]].rolling(int(252.0 / 4.0)).mean()
        xBase["rollingMean6m"] = xBase[[stock]].rolling(int(252.0 / 2.0)).mean()
        xBase = xBase.iloc[-1:]  #
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
        # print(xBase.shape, dff.shape, moment.shape)
        # process data to add labels
        dff["Date"] = pd.to_datetime(dff.Date)
        dffL = dff
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
        dffL = dffL.fillna(0)
        predictionPoint = dff.iloc[-1:]
        predictionPoint = predictionPoint[
            ["rollingMean4m", "rollingMean2m", "rollingMean6m", "momentum"]
        ]
        # predictionPoint = (predictionPoint - features.min()) / (
        #   features.max() - features.min()
        # )
        print(predictionPoint)
        y_pred = model.predict(predictionPoint)
        ##print(predictionPoint)
        ##print(y_pred)
        predictions.append({"stock": stock, "prediction": y_pred[0], "modelError": mae})
    except Exception as e:
        ##print(e)
        # print(stock)
        continue

print(pd.DataFrame(predictions))
df = pd.DataFrame(predictions)
df.to_csv("./data/expectedReturnsLGBM.csv", index=False)
print(df.sort_values(by=["prediction"], ascending=False))
czr 46   1000/46
wbd 15  1000/15
ccl 11 1000/11
ua 9  1000/9
CTRA 34 1000/34