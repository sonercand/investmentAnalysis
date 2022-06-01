"""
consider factors below to estimate returns in the end of next 4 months where 4 months is the time to rebalance portfolio:
    quality: financially healthy firms : earning consistency, lower dept to equity
    value: in expensive stocks: lower P/E (price/earning)  and P/B price/carrying value on balance sheet.
    momentum: trending stocks : Price appreciation
    size: smaller companies lower market cap

build a model predicting returns in 4 months using factors above + previous returns
using those expected returns optimise returns/risk ratio and allocate weights to assests.

train models:
model per stock or a deep layered network for all:
    E[p] = f(factors)
    windows = [w1=[t0..t0+4months],w2=[t0+1day + t0+1day+4months]]
testing the model:
    start from a cutoff point: 


"""
