import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas_datareader.data as web
from datetime import datetime
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


tic = "TSLA"

start = "2020-01-01"

end = "2022-05-03"

df = web.DataReader(tic, "yahoo", start=start, end=end)
df["daily_return"] = df["Close"].pct_change(1)


app = dash.Dash()

app.layout = html.Div(
    [
        html.H1("Stock Price and Daily Return for {}".format(tic), id="page_title"),
        html.Div(
            [
                html.H3("Enter a stock symbol:", style={"paddingRight": "30px"}),
                dcc.Input(id="stock_picker", value=[tic]),
            ],
            style={"display": "inline-block", "verticalAlign": "top", "width": "30%"},
        ),
        dcc.Graph(
            id="graph",
            figure={
                "data": [{"x": df.index, "y": df["Close"], "name": tic}],
                "layout": {"title": "Stock Price"},
            },
        ),
        dcc.Graph(
            id="graph_return",
            figure={
                "data": [{"x": df.index, "y": df["daily_return"], "name": tic}],
                "layout": {"title": "Stock Daily Return"},
            },
        ),
    ]
)


@app.callback(
    Output("page_title", "children"),
    [Input("stock_picker", "value")],
)
def update_title(stock_picker):
    return "Stock Price and Daily Return for {}".format(stock_picker)


@app.callback(
    Output("graph", "figure"),
    [
        Input("stock_picker", "value"),
    ],
)
def update_graph(stock_ticker):
    start = "2020-01-01"
    end = "2022-05-03"
    df = web.DataReader(str(stock_ticker), "yahoo", start=start, end=end)

    fig = {
        "data": [{"x": df.index, "y": df["Close"], "name": stock_ticker}],
        "layout": {"title": stock_ticker},
    }
    return fig


@app.callback(
    Output("graph_return", "figure"),
    [
        Input("stock_picker", "value"),
    ],
)
def update_graph_return(stock_ticker):
    start = "2020-01-01"
    end = "2022-05-03"
    df = web.DataReader(str(stock_ticker), "yahoo", start=start, end=end)
    df["daily_return"] = df["Close"].pct_change(1)
    fig = {
        "data": [{"x": df.index, "y": df["daily_return"], "name": stock_ticker}],
        "layout": {"title": "Daily Return for " + str(stock_ticker)},
    }
    return fig


if __name__ == "__main__":
    app.run_server()
