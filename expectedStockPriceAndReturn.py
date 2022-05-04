import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.autograd import Variable
from sklearn.preprocessing import MinMaxScaler
import pandas_datareader.data as web

tic = "TSLA"
start = "2021-05-03"
end = "2022-05-03"
df = web.DataReader(tic, "yahoo", start=start, end=end)
df.reset_index()
training_set = df[["Close"]].values


def sliding_windows(data, seq_length):
    x = []
    y = []

    for i in range(len(data) - seq_length - 1):
        _x = data[i : (i + seq_length)]
        _y = data[i + seq_length]
        x.append(_x)
        y.append(_y)

    return np.array(x), np.array(y)


sc = MinMaxScaler()
training_data = sc.fit_transform(training_set)
seq_length = 10
x, y = sliding_windows(training_data, seq_length)
