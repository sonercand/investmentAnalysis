from cmath import exp
from tkinter import W
import pandas as pd
import json
from Calculations.portfolioOptimisation import OptimisePortfolio
from multiprocessing import Pool, Process
import numpy as np

riskRange = [0, 0.4]
data = pd.read_csv("./data/snpFtseClose.csv")

sectors = ["BATS.L", "IMB.L", "MO", "PM"]
sectors = [sectors]
stocks = [item for sublist in sectors for item in sublist]

stocks.append("Date")
data = data[stocks]
from Calculations.portfolioAnalytics import getName

sectors = ["BATS.L", "IMB.L", "MO", "PM"]
for stock in sectors:
    print(stock)
    print(getName(stock))
