from cmath import exp
from tkinter import W
import pandas as pd
import json
from Calculations.portfolioOptimisation import OptimisePortfolio
from multiprocessing import Pool, Process
import numpy as np

riskRange = [0, 0.4]
data = pd.read_csv("./data/snpFtseClose.csv")
print(data.shape)
data = data.drop(columns=["Unnamed: 0.1", "Unnamed: 0"], axis=1)
data = data.dropna(axis=1, how="all")
print(data)
print(data.columns)
data.to_csv("./data/snpFtseClose.csv", index=False)
# data["Date"] = pd.to_datetime(data["Date"])
# data.set_index("Date", inplace=True)
# data.sort_index(inplace=True)
# data.rename(columns={"Unnamed: 0": "Date"}, inplace=True)
