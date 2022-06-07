"""
# Estimate expected asset price using ml
* features are: balance sheets, income balance for the last 5 years and momentum
* scope: portfolio will be reallocated every 13 weeks therefore every 13 weeks returns should be estimated for the next reallocation date.



"""
from pyexpat import features
import pandas as pd
from pandasql import sqldf
from datetime import timedelta

adjC = pd.read_csv("./data/snpFtseClose.csv")
# filter for snp500
cols = list(adjC.columns)

cols = [col for col in cols if not col.upper().endswith(".L")]
adjC = adjC[cols]


# replace nan
adjC["Date"] = pd.to_datetime(adjC.Date)
adjC = adjC.sort_values(by=["Date"])
adjC.ffill(inplace=True)
adjC.bfill(inplace=True)
# get Y values for train,val and test######################
# date range: 2017-05-25 to 2022-05-24 (5 years)

# 13 weeks in terms of 13 work days is 252/4

# yLabel = adjC.loc[252 / 2 :]  # 2 times 13 weeks


# features##################################################
# lets do it for one stock
stock = "MMM"
yLabel = adjC[[stock, "Date"]]

bsF = pd.read_csv("./data/balanceFeatures.csv")
bsF["fiscalDateEnding"] = pd.to_datetime(bsF["fiscalDateEnding"])
bsF_sub = bsF[bsF.ticker == stock]
xBase = adjC[["Date", stock]]
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
# join income statements #####################
isF = pd.read_csv("./data/incomeFeatures.csv")
isF_sub = isF[isF.ticker == stock]
isF_sub["fiscalDateEnding"] = pd.to_datetime(isF_sub["fiscalDateEnding"])
query = """
with get_data as (
    select t1.*,t2.* from dfm t1 left join isF_sub t2 on t2.fiscalDateEnding<=t1.Date
)select distinct gd.* from get_data gd inner join(select Date, max(fiscalDateEnding) as max_ from get_data group by Date) t3 on
t3.Date = gd.Date and t3.max_ =gd.fiscalDateEnding
"""
dfa = pysqldf(query)


# join rolling momentum #######################
moment = pd.read_csv("./data/momentumSNP.csv")
moment = moment[["Date", stock]]
moment["Date"] = pd.to_datetime(moment["Date"])
query = """
    select t1.*,t2.{} as momentum from dfa t1 left  join moment t2 on t1.Date== t2.Date
""".format(
    stock
)
dff = pysqldf(query)

dff["Date"] = pd.to_datetime(dff.Date)
dff["labelDate"] = dff["Date"] + timedelta(days=int(252 / 4))

query = """
with get_data as ( select * from dff)
select gd.*,t2.{} as label from get_data gd left join (select  Date,{} from get_data) t2 on gd.labelDate=t2.Date
""".format(
    stock, stock
)
dffL = pysqldf(query)
# dffL.dropna(inplace=True)
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

features_and_labels = dffL[features_cols]
# replace na
features_and_labels = features_and_labels[
    features_and_labels["label"].notna()
]  # remove rows that have no label

features_and_labels = features_and_labels.dropna()
from sklearn import preprocessing

mm_scaler = preprocessing.MinMaxScaler()
features = features_and_labels[features_cols].values
labels = features_and_labels["label"].values
features = mm_scaler.fit_transform(features)


# model
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint


bst_model_path = "./data/modeldata/{}.h5".format(stock)
model_checkpoint = ModelCheckpoint(
    bst_model_path, save_best_only=True, save_weights_only=True
)

model = keras.Sequential(
    [
        layers.Dense(128, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(32, activation="relu"),
        layers.Dense(8, activation="relu"),
        layers.Dense(2, activation="relu"),
        layers.BatchNormalization(),
        layers.Dense(1),
    ]
)

model.compile(loss="mean_absolute_error", optimizer=tf.keras.optimizers.Adam(0.05))
print(model.summary())
history = model.fit(
    features,
    labels,
    epochs=400,
    # Suppress logging.
    verbose=0,
    validation_split=0.2,
    callbacks=[model_checkpoint],
)
model.load_weights(bst_model_path)
hist = pd.DataFrame(history.history)
hist["epoch"] = history.epoch
print(hist.tail(20))
test_r = {}
test_r["test_results"] = model.evaluate(features, labels, verbose=0)

print(test_r)
test_predictions = model.predict(features).flatten()
print(labels)
print(test_predictions)
