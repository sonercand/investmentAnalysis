from modelDataProcessing import get_dataset, split_dataset, WindowGenerator
from model import FeedBack, compile_and_fit
import tensorflow as tf
from datetime import datetime, timedelta
import numpy as np


def trainAndPredict(tic, days_to_predict):
    stock_ticker = tic
    today_ = str(datetime.today().strftime("%Y-%m-%d"))
    days = timedelta(365 * 5)
    start = datetime.today() - days
    start = str(start.strftime("%Y-%m-%d"))
    dataset = get_dataset(stock_ticker, start, today_)
    days_to_predict = int(days_to_predict)
    # constract days

    dates = []
    for k in range(days_to_predict):
        new_date = datetime.today() + timedelta(k)
        dates.append(new_date.date())

    # normalise and split dataset
    df_train, df_val, df_test = split_dataset(dataset, train_ratio=0.8, val_ratio=0.1)
    train_mean = df_train.mean()
    train_std = df_train.std()
    df_train = (df_train - train_mean) / train_std
    df_val = (df_val - train_mean) / train_std
    df_test = (df_test - train_mean) / train_std

    # use 30 days of data to predict next 5 days
    OUT_STEPS = int(days_to_predict)
    input_width = (
        OUT_STEPS * 10
    )  # number of days to use for predicting out_steps days in the future
    multi_window = WindowGenerator(
        input_width=input_width,
        label_width=OUT_STEPS,
        shift=OUT_STEPS,
        train_df=df_train,
        val_df=df_val,
        test_df=df_test,
        label_columns=["Close"],
    )

    feedback_model = FeedBack(units=128, out_steps=OUT_STEPS)
    history = compile_and_fit(feedback_model, multi_window)  # train model
    # /training over
    # start prediction
    data = (dataset - train_mean) / train_std
    data = np.array(data, dtype=np.float32)
    data = data[len(data) - input_width :]

    ds = tf.keras.utils.timeseries_dataset_from_array(
        data=data,
        targets=None,
        sequence_length=input_width,
        sequence_stride=1,
        shuffle=False,
        batch_size=1,
    )
    prediction = feedback_model.predict(ds)
    results = [p * train_std + train_mean for p in prediction.flatten()]
    results = [r[0] for r in results]
    return results, dataset, stock_ticker, dates, input_width
