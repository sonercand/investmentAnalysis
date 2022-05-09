from venv import create
import pandas_datareader.data as web

# import numpy as np
# import tensorflow as tf
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from utils import StockMarketInformation as SMI
from calcBeta import calculateBetaUsingYFinance
import plotly.graph_objs as go
from capitalAssetPricingModel import calculateCAPMviaDfs
from widgets import (
    createCompanyInfoWidget,
    createStockPricePlot,
    createStockVsMarketWidget,
    createStockVsMarketGraph,
    createStockSelectionWidget,
    createSustainabilityWidget,
)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


# Default Data

tic = "MNG.L"
period = "2y"
smi = SMI(sandbox=False, tic=tic)
ci = smi.getCompanyInfo()

if ci["country"] == "GB":
    market = "L"
    marketIndex = "^FTMC"
else:
    market = "US"
    marketIndex = "^GSPC"

smiMarket = SMI(sandbox=False, tic=marketIndex)
closeDataMarket = smiMarket.getHistoricalData(period=period)
closeData = smi.getHistoricalData(period=period)
beta = calculateBetaUsingYFinance(closeData, closeDataMarket)
expectedReturn = calculateCAPMviaDfs(closeDataMarket, beta)
stockList = smi.getStockSymbols(exchange=market)
stocks = smi.getStockSymbolList(stockList)
companyName = ci["name"]
companyCountry = ci["country"]
exchange = ci["exchange"]
industry = ci["finnhubIndustry"]
ipo = ci["ipo"]
logo = ci["logo"]
mCapitalisation = ci["marketCapitalization"]
imageSource = ci["logo"]


# load widgets ---------------------------
stockSelectionWidget = createStockSelectionWidget(stocks, tic, id="stock_picker")
companyInfoWidget = createCompanyInfoWidget(
    imageSource, companyName, exchange, industry, mCapitalisation, ipo, id="companyInfo"
)
stockPriceGraph = createStockPricePlot(closeData, tic, id="stockPriceGraph")
stockVsMarketWidget = createStockVsMarketWidget(
    beta, expectedReturn, id="stockVsMarketVidget"
)

stockPriceVsMarketGraph = createStockVsMarketGraph(
    closeDataMarket, closeData, tic, id="stockVsMarketGraph"
)

susWidget = createSustainabilityWidget(smi, tic)
# Layout ---------------------------------
app.layout = html.Div(
    [
        dbc.Container(
            [
                stockSelectionWidget,
                dbc.Row(
                    [
                        html.H2("General Info"),
                        dbc.Col([companyInfoWidget], width=2),
                        dbc.Col([stockPriceGraph], width=10),
                    ],
                    style={"border": "solid", "borderWidth": "1px", "padding": "1em"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [html.H2("Stock vs Market"), stockVsMarketWidget],
                            width=2,
                        ),
                        dbc.Col([stockPriceVsMarketGraph], width=10),
                    ],
                    style={"border": "solid", "borderWidth": "1px", "padding": "1em"},
                ),
                dbc.Row(
                    dbc.Col(
                        [susWidget],
                        style={
                            "border": "solid",
                            "borderWidth": "1px",
                            "padding": "1em",
                        },
                    )
                ),
            ]
        )
    ]
)


@app.callback(
    [
        Output("companyInfo", "children"),
        Output("stockPriceGraph", "children"),
        Output("stockVsMarketGraph", "children"),
        Output("sus", "children"),
    ],
    [Input("stock_picker", "value")],
)
def update_graph(stock_ticker):
    try:
        tic = stock_ticker[-1]
    except:
        tic = stock_ticker

    period = "2y"
    smi = SMI(sandbox=False, tic=tic)
    ci = smi.getCompanyInfo()
    companyName = ci["name"]

    exchange = ci["exchange"]
    industry = ci["finnhubIndustry"]
    ipo = ci["ipo"]
    mCapitalisation = ci["marketCapitalization"]
    imageSource = ci["logo"]
    closeDataMarket = smiMarket.getHistoricalData(period=period)
    closeData = smi.getHistoricalData(period=period)

    return [
        createCompanyInfoWidget(
            imageSource,
            companyName,
            exchange,
            industry,
            mCapitalisation,
            ipo,
            id="companyInfo",
        ),
        createStockPricePlot(closeData, tic, id="stockPriceGraph"),
        createStockVsMarketGraph(
            closeDataMarket, closeData, tic, id="stockVsMarketGraph"
        ),
        createSustainabilityWidget(smi, tic, id="sus"),
    ]


if __name__ == "__main__":
    app.run_server(debug=True)
