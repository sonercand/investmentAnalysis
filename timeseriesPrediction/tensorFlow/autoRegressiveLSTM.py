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

OUT_STEPS = 5
multi_window = WindowGenerator(
    input_width=30,
    label_width=OUT_STEPS,
    shift=OUT_STEPS,
    train_df=df_train,
    val_df=df_val,
    test_df=df_test,
    label_columns=["Close"],
)

print(multi_window)


class MultiStepLastBaseline(tf.keras.Model):
    def call(self, inputs):
        return tf.tile(inputs[:, -1:, :], [1, OUT_STEPS, 1])


last_baseline = MultiStepLastBaseline()
last_baseline.compile(
    loss=tf.losses.MeanSquaredError(), metrics=[tf.metrics.MeanAbsoluteError()]
)

multi_val_performance = {}
multi_performance = {}

multi_val_performance["Last"] = last_baseline.evaluate(multi_window.val)
multi_performance["Last"] = last_baseline.evaluate(multi_window.test, verbose=0)
# multi_window.plot(last_baseline)


# lstm model
class FeedBack(tf.keras.Model):
    def __init__(self, units, out_steps):
        super().__init__()
        self.out_steps = out_steps
        self.units = units
        self.lstm_cell = tf.keras.layers.LSTMCell(units)
        # Also wrap the LSTMCell in an RNN to simplify the `warmup` method.
        self.lstm_rnn = tf.keras.layers.RNN(self.lstm_cell, return_state=True)
        self.dense = tf.keras.layers.Dense(1)

    def warmup(self, inputs):
        # inputs.shape => (batch, time, features)
        # x.shape => (batch, lstm_units)
        x, *state = self.lstm_rnn(inputs)

        # predictions.shape => (batch, features)
        prediction = self.dense(x)
        return prediction, state

    def call(self, inputs, training=None):
        # Use a TensorArray to capture dynamically unrolled outputs.
        predictions = []
        # Initialize the LSTM state.
        prediction, state = self.warmup(inputs)

        # Insert the first prediction.
        predictions.append(prediction)

        # Run the rest of the prediction steps.
        for n in range(1, self.out_steps):
            # Use the last prediction as input.
            x = prediction
            # Execute one lstm step.
            x, state = self.lstm_cell(x, states=state, training=training)
            # Convert the lstm output to a prediction.
            prediction = self.dense(x)
            # Add the prediction to the output.
            predictions.append(prediction)

        # predictions.shape => (time, batch, features)
        predictions = tf.stack(predictions)
        # predictions.shape => (batch, time, features)
        predictions = tf.transpose(predictions, [1, 0, 2])
        return predictions


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


feedback_model = FeedBack(units=128, out_steps=OUT_STEPS)

history = compile_and_fit(feedback_model, multi_window)

multi_val_performance["AR LSTM"] = feedback_model.evaluate(multi_window.val)
multi_performance["AR LSTM"] = feedback_model.evaluate(multi_window.test, verbose=0)
# multi_window.plot(feedback_model)


# final test
dataset = get_dataset("TSLA", "2022-02-03", "2022-05-04")
print(dataset.shape)
print(dataset.tail())

data = (dataset - train_mean) / train_std

data = np.array(data, dtype=np.float32)
data = data[len(data) - 30 :]
print(data.shape)

ds = tf.keras.utils.timeseries_dataset_from_array(
    data=data,
    targets=None,
    sequence_length=30,
    sequence_stride=1,
    shuffle=False,
    batch_size=1,
)
print(ds)


prediction = feedback_model.predict(ds)
print(prediction)

results = [p * train_std + train_mean for p in prediction.flatten()]
print(results)
