"""Only for S&P500"""
import pandas as pd

aClose = pd.read_csv(".\data\snpFtseClose.csv")  # adjusted close data set
print(aClose.Date.min())
