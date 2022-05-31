"""
from dash import dash, dcc, html, Input, Output, State, callback, callback_context
import dash_bootstrap_components as dbc
from pages import navigation
from dotenv import load_dotenv
import yfinance as yf
import finnhub as fh
import os
import numpy as np
from datetime import datetime, timedelta
from Calculations.portfolioAnalytics import (
    getData,
    getDailyReturns,
    calcWeights,
    portfolioSTD,
    expectedPortfolioReturn,
)
import json

EXCHANGES = ["US", "L"]
load_dotenv()
api_key = os.getenv("FINHUB_API_KEY")
finnhub_client = fh.Client(api_key=api_key)
tickerList = []
for exchange in EXCHANGES:
    items = finnhub_client.stock_symbols(exchange)
    list_ = [item["symbol"] for item in items]
    tickerList += list_

# colors
color1 = "#4990C2"
# Layout ---------------------------------


layout = html.Div(
    [
        navigation.navbar,
        html.Div(
            [
                dbc.Row(
                    [
                        html.H2(
                            "Generic Analysis for Learning Purposes",
                            style={
                                "color": color1,
                                "textAlign": "center",
                                "padding": "3em",
                            },
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2("select Stocks"),
                                dcc.Dropdown(
                                    id="dropdown",
                                    options=tickerList,
                                    value=[],
                                    multi=True,
                                    style={"padding": "1em"},
                                ),
                                html.H2("Set the weights"),
                                dcc.Textarea(
                                    style={"width": "100%", "height": 100},
                                    id="textArea",
                                ),
                                dbc.Button(
                                    id="setPortfolio",
                                    n_clicks=0,
                                    children="set portfolio!",
                                    style={
                                        "background": color1,
                                        "width": "80%",
                                        "margin-left": "10%",
                                        "margin-top": "0",
                                    },
                                ),
                            ],
                            width=2,
                        ),
                        dbc.Col(
                            [
                                html.Div([], id="portfolioStats"),
                                html.Div([], id="stockPriceGraph1"),
                            ],
                            width=10,
                        ),
                    ]
                ),
            ],
            style={"width": "95%", "margin": "0 auto"},
        ),
    ]
)


@callback(
    Output("stockPriceGraph1", "children"),
    [State("dropdown", "value")],
    [Input("setPortfolio", "n_clicks")],
)
def plotStocks(stockList, n_clicks):
    if n_clicks > 0:
        widgets = []
        print("start plotStocks")
        data = getData(stockList, "1y")
        print("finish get data")
        traces = []
        traces2 = []
        print(data.columns)
        for col in data.columns:
            traces.append(
                {
                    "x": data.index,
                    "y": ((data[col] - data[col].mean()) / data[col].std()),
                    "name": col,
                }
            )
            traces2.append(
                {
                    "x": data.index,
                    "y": ((data[col] - data[col].iloc[0])),
                    "name": col,
                }
            )

        widget1 = dcc.Graph(
            id="graphNormPrice",
            figure={
                "data": traces,
                "layout": {"title": "Normalised Daily Stock Prices"},
            },
            style={"marginTop": "1em"},
        )
        widget2 = dcc.Graph(
            id="relativePrice",
            figure={
                "data": traces2,
                "layout": {"title": "Relative Stock Prices"},
            },
            style={"marginTop": "1em"},
        )
        widgets.append(widget1)
        widgets.append(widget2)
        return widgets


@callback(
    Output("portfolioStats", "children"),
    [State("dropdown", "value"), State("textArea", "value")],
    [Input("setPortfolio", "n_clicks")],
)
def calcPortfolioStats(stockList, textValue, n_clicks):
    if n_clicks > 0:
        rw = textValue.split(",")
        rw = [float(r) for r in rw]
        data = getData(stockList, period="1y")
        weights = calcWeights(rw)
        dailyReturns = getDailyReturns(data)
        stdPortAnnual, indStockAnnualStd = portfolioSTD(dailyReturns, weights)
        pReturn = expectedPortfolioReturn(data, rw)
        table_header = [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Annual Expected Return"),
                        html.Th("Annual Expected Std(Risk)"),
                    ]
                )
            )
        ]
        row1 = html.Tr([html.Td(pReturn), html.Td(stdPortAnnual)])
        table_body = [html.Tbody([row1])]
        table = dbc.Table(
            table_header + table_body, bordered=True, style={"textAlign": "center"}
        )
        table_header2 = [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Stock"),
                        html.Th("Individual Annual Risk"),
                    ]
                )
            )
        ]
        rows = []
        df1 = indStockAnnualStd.reset_index()
        df1.columns = ["stock", "risk"]
        rows = []
        for index, row in df1.iterrows():
            row = html.Tr([html.Td(row["stock"]), html.Td(row["risk"])])
            rows.append(row)
        table_body2 = [html.Tbody(rows)]
        table2 = dbc.Table(
            table_header2 + table_body2, bordered=True, style={"textAlign": "center"}
        )
        # plot best worst and likely scenarios
        initial_amount = np.sum(rw)
        best_case = initial_amount * (1 + pReturn + stdPortAnnual)
        worst_case = initial_amount * (1 + pReturn - stdPortAnnual)
        excpected = initial_amount * (1 + pReturn)
        traces = []
        traces.append(
            {
                "x": [datetime.today(), datetime.today() + timedelta(365)],
                "y": [initial_amount, excpected],
                "name": "Expected Amount",
            }
        )
        traces.append(
            {
                "x": [datetime.today(), datetime.today() + timedelta(365)],
                "y": [initial_amount, worst_case],
                "name": "Worst Case",
            }
        )
        traces.append(
            {
                "x": [datetime.today(), datetime.today() + timedelta(365)],
                "y": [initial_amount, best_case],
                "name": "Best Case",
            }
        )
        graph = dcc.Graph(
            id="returns",
            figure={
                "data": traces,
                "layout": {
                    "title": "Value in a year if you start with {}".format(
                        initial_amount
                    )
                },
            },
            style={"marginTop": "1em"},
        )
        return [table, table2, graph]
"""
