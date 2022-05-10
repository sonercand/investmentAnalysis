from venv import create
import pandas_datareader.data as web

# import numpy as np
# import tensorflow as tf
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from utils import StockMarketInformation as SMI, getExchanges
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
    createMarketSelectionWidget,
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# exhcanges options and default values
exchange_dict = getExchanges()
exchangeOptions = list(exchange_dict.keys())
print(exchangeOptions)
defaultExchange = "US exchanges (NYSE, Nasdaq)"
defaultExchangeCode = exchange_dict[defaultExchange]
# default stock and stock selection options
tic = "AAPL"
period = "2y"
smi = SMI(sandbox=False, tic=tic)
stockList = smi.getStockSymbols(exchange=defaultExchangeCode)
stocks = smi.getStockSymbolList(
    stockList
)  # stock selection options for a given exchange market
# default company info
ci = smi.getCompanyInfo(tic=tic)

# set market index for comparisions
if ci["country"] == "GB":
    market = "L"
    marketIndex = "^FTMC"
elif ci["country"] == "US":
    market = "US"
    marketIndex = "^GSPC"
else:  # set market index to us for the rest of the stocks
    market = "US"
    marketIndex = "^GSPC"
# get default historical data
closeDataMarket = smi.getHistoricalData(period=period, tic=marketIndex)
closeData = smi.getHistoricalData(period=period, tic=tic)
beta = calculateBetaUsingYFinance(closeData, closeDataMarket)
expectedReturn = calculateCAPMviaDfs(closeDataMarket, beta)

# organise default company info
companyName = ci["name"]
companyCountry = ci["country"]
exchange = ci["exchange"]
industry = ci["finnhubIndustry"]
ipo = ci["ipo"]
logo = ci["logo"]
mCapitalisation = ci["marketCapitalization"]
imageSource = ci["logo"]


# load widgets ---------------------------
exchangeSelectionWidget = createMarketSelectionWidget(
    exchangeOptions=exchangeOptions,
    defaultExchange=defaultExchange,
    id="market_picker",
)
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

susWidget = createSustainabilityWidget(smi, tic, id="sus")

# colors
color1 = "#4990C2"
# Layout ---------------------------------
app.layout = html.Div(
    [
        html.Div(
            [
                dbc.Row(
                    [
                        html.H2(
                            "General Stock Analysis and Information",
                            style={
                                "color": color1,
                                "textAlign": "center",
                                "padding": "3em",
                            },
                        ),
                        html.Br(),
                        dbc.Col(
                            [
                                exchangeSelectionWidget,
                                dbc.Button(
                                    "Select the Exchange",
                                    id="submit-val",
                                    n_clicks=0,
                                    style={
                                        "background": color1,
                                        "width": "80%",
                                        "margin-left": "10%",
                                        "margin-top": "0",
                                    },
                                ),
                                stockSelectionWidget,
                                dbc.Button(
                                    "Select Stock",
                                    id="submit-stock-val",
                                    n_clicks=0,
                                    style={
                                        "background": color1,
                                        "width": "80%",
                                        "margin-left": "10%",
                                        "margin-top": "0",
                                    },
                                ),
                            ],
                            width=2,
                            style={
                                "border": "solid",
                                "border-width": "1px",
                                "border-color": color1,
                            },
                        ),
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    [
                                        dbc.Tab(
                                            dbc.Row(
                                                [
                                                    html.H2(
                                                        "General Info",
                                                        style={"color": color1},
                                                    ),
                                                    dbc.Col(
                                                        [companyInfoWidget], width=2
                                                    ),
                                                    dbc.Col(
                                                        [stockPriceGraph], width=10
                                                    ),
                                                ],
                                                style={
                                                    "padding": "1em",
                                                    "border": "none",
                                                },
                                            ),
                                            label="General Info",
                                        ),
                                        dbc.Tab(
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.H2(
                                                                "Stock vs Market",
                                                                style={"color": color1},
                                                            ),
                                                            stockVsMarketWidget,
                                                        ],
                                                        width=2,
                                                    ),
                                                    dbc.Col(
                                                        [stockPriceVsMarketGraph],
                                                        width=10,
                                                    ),
                                                ],
                                                style={
                                                    "padding": "1em",
                                                },
                                            ),
                                            label="Beta",
                                        ),
                                        dbc.Tab(
                                            dbc.Row(
                                                dbc.Col(
                                                    [susWidget],
                                                    style={
                                                        "padding": "1em",
                                                    },
                                                )
                                            ),
                                            label="Sustainability",
                                            style={"color": "white"},
                                        ),
                                    ],
                                    style={
                                        "background": "rgba(73, 144, 194,1)",
                                        "color": "white",
                                    },
                                ),
                            ],
                            width=10,
                            style={
                                "border": "solid",
                                "border-width": "1px",
                                "border-color": color1,
                                "padding": "0",
                            },
                        ),
                    ]
                )
            ],
            style={"width": "95%", "margin": "0 auto"},
        )
    ]
)


@app.callback(
    Output("stock_picker_parent", "children"),
    [State("market_picker", "value")],
    Input("submit-val", "n_clicks"),
)
def update_stocklist(market_picker_value, n_clicks):
    if n_clicks > 0:
        marketCode = exchange_dict[market_picker_value]
        stockList = smi.getStockSymbols(exchange=marketCode)
        stocks = smi.getStockSymbolList(stockList)
        tic = stocks[0]
        stockSelectionWidget = createStockSelectionWidget(
            stocks, tic, id="stock_picker"
        )
        return stockSelectionWidget


@app.callback(
    [
        Output("companyInfo", "children"),
        Output("stockPriceGraph", "children"),
        Output("stockVsMarketGraph", "children"),
        Output("sus", "children"),
        Output("stockVsMarketWidget_parent", "children"),
    ],
    [State("stock_picker", "value")],
    [Input("submit-stock-val", "n_clicks")],
)
def update_graph(stock_ticker, n_clicks):
    if n_clicks > 0:
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
        closeDataMarket = smi.getHistoricalData(period=period, tic=marketIndex)
        closeData = smi.getHistoricalData(period=period, tic=tic)
        beta = calculateBetaUsingYFinance(closeData, closeDataMarket)
        expectedReturn = calculateCAPMviaDfs(closeDataMarket, beta)
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
            createStockVsMarketWidget(beta, expectedReturn, id="stockVsMarketVidget"),
        ]


if __name__ == "__main__":
    app.run_server(debug=True)
