import pandas_datareader.data as web
import numpy as np
from torch import lstm
from dataProcessing import WindowGenerator, get_dataset, split_dataset
import tensorflow as tf

dataset = get_dataset("TSLA", "2018-04-03", "2022-04-03")
print(dataset.shape)
df_train, df_val, df_test = split_dataset(dataset, train_ratio=0.7, val_ratio=0.2)
train_mean = df_train.mean()
train_std = df_train.std()

df_train = (df_train - train_mean) / train_std
df_val = (df_val - train_mean) / train_std
df_test = (df_test - train_mean) / train_std

single_step_window = WindowGenerator(
    input_width=10,
    label_width=10,
    shift=1,
    train_df=df_train,
    val_df=df_val,
    test_df=df_test,
    label_columns=["Close"],
)
print(single_step_window)
for example_inputs, example_labels in single_step_window.train.take(1):
    print(f"Inputs shape (batch, time, features): {example_inputs.shape}")
    print(f"Labels shape (batch, time, features): {example_labels.shape}")

# Baseline model use previous value as prediction
class Baseline(tf.keras.Model):
    def __init__(self, label_index=None):
        super().__init__()
        self.label_index = label_index

    def call(self, inputs):
        if self.label_index is None:
            return inputs
        result = inputs[:, :, self.label_index]
        return result[:, :, tf.newaxis]


baseline = Baseline(label_index=0)

baseline.compile(
    loss=tf.losses.MeanSquaredError(), metrics=[tf.metrics.MeanAbsoluteError()]
)

val_performance = {}
performance = {}
val_performance["Baseline"] = baseline.evaluate(single_step_window.val)
performance["Baseline"] = baseline.evaluate(single_step_window.test, verbose=0)
single_step_window.plot(baseline)

# LSTM MODEL
lstm_model = tf.keras.models.Sequential(
    [
        # Shape [batch, time, features] => [batch, time, lstm_units]
        tf.keras.layers.LSTM(32, return_sequences=True),
        # Shape => [batch, time, features]
        tf.keras.layers.Dense(units=1),
    ]
)


def compile_and_fit(model, window, patience=2, max_epochs=100):
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=patience, mode="min"
    )

    model.compile(
        loss=tf.losses.MeanSquaredError(),
        optimizer=tf.optimizers.Adam(),
        metrics=[tf.metrics.MeanAbsoluteError()],
    )

    history = model.fit(
        window.train,
        epochs=max_epochs,
        validation_data=window.val,
        callbacks=[early_stopping],
    )
    return history


history = compile_and_fit(lstm_model, single_step_window)

val_performance["LSTM"] = lstm_model.evaluate(single_step_window.val)
performance["LSTM"] = lstm_model.evaluate(single_step_window.test, verbose=0)
single_step_window.plot(lstm_model)
