import pandas_datareader.data as web
import numpy as np
from torch import lstm
from dataProcessing import WindowGenerator, get_dataset, split_dataset
import tensorflow as tf
from model import FeedBack, compile_and_fit
from datetime import datetime, timedelta
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

tic = "TSLA"
today_ = str(datetime.today().strftime("%Y-%m-%d"))
days = timedelta(365 * 5)
start = datetime.today() - days
start = str(start.strftime("%Y-%m-%d"))
df = get_dataset(tic, start, today_)
df["daily_return"] = df["Close"].pct_change(1)

jumbotron = html.Div(
    dbc.Container(
        [
            html.H1(
                "Stock Prices - Daily Returns and Predictions", className="display-3"
            ),
            html.P(
                "Start typing a ticker, graphs will be automatically updated.",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P("This is only for test purposes. "),
            html.P("Model used for predictions: Autoregressive LSTM."),
            html.P(
                "10*X historic data points needed to predict stock prices for X many days. "
            ),
            html.P("Data source: yahoo finance"),
            html.P(dbc.Button("Learn more", color="primary"), className="lead"),
        ],
        fluid=True,
        className="py-3",
        style={"padding": "3em"},
    ),
    className="p-3 bg-light rounded-3",
)
dummy_div = html.Div([], style={"margin": "1em", "height": "2em"})
app.layout = html.Div(
    [
        dbc.Container(
            [
                jumbotron,
                dummy_div,
                dbc.Row(
                    [
                        dbc.Col([]),
                        dbc.Col(
                            [
                                html.H3(
                                    "Enter a stock symbol:",
                                    style={"textAlign": "center"},
                                ),
                                dbc.Input(
                                    id="stock_picker",
                                    value=tic,
                                    className="p-3 bg-light rounded-3",
                                    style={"padding": "3em"},
                                ),
                            ],
                            style={"padding": "4em"},
                        ),
                        dbc.Col([]),
                    ],
                ),
                html.H2(
                    "Stock Price and Daily Return for {}".format(tic),
                    id="page_title",
                    style={"textAlign": "center"},
                ),
                dummy_div,
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3(
                                    "Daily Stock Prices", style={"margin-top": "38%"}
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="graph",
                                    figure={
                                        "data": [
                                            {
                                                "x": df.index,
                                                "y": df["Close"],
                                                "name": tic,
                                            }
                                        ],
                                        "layout": {"title": "Stock Price"},
                                    },
                                ),
                            ]
                        ),
                    ]
                ),
                dummy_div,
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="graph_return",
                                    figure={
                                        "data": [
                                            {
                                                "x": df.index,
                                                "y": df["daily_return"],
                                                "name": tic,
                                            }
                                        ],
                                        "layout": {"title": "Stock Daily Return"},
                                    },
                                ),
                            ],
                            width=9,
                        ),
                        dbc.Col(
                            [html.H3("Daily Returns", style={"margin-top": "38%"})],
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3(
                                    "Use slider to select number of days to predict ",
                                    id="predict_title",
                                    style={"margin-top": "10%"},
                                ),
                                dcc.Slider(5, 50, 5, value=5, id="daysToPredict"),
                                dbc.Button(
                                    id="predictButton",
                                    n_clicks=0,
                                    children="Run Prediction!",
                                    color="success",
                                ),
                            ],
                            width=3,
                            style={"margin-top": "10%"},
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="prediction_graph",
                                    figure={},
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            fluid=True,
            style={
                "padding": "3em",
                "margin-right": "2%",
                "margin-left": "2%",
                "width": "95%",
                "color": "#4890C1",
            },
        )
    ]
)


@app.callback(
    Output("prediction_graph", "figure"),
    [Input("predictButton", "n_clicks")],
    [State("stock_picker", "value"), State("daysToPredict", "value")],
)
def update_prediction_graph(n_clicks, stock_ticker, days_to_predict):
    if n_clicks < 1:
        return {}
    dataset = get_dataset(stock_ticker, start, today_)
    days_to_predict = int(days_to_predict)
    # constract days

    dates = []
    for k in range(days_to_predict):
        new_date = datetime.today() + timedelta(k)
        dates.append(new_date.date())
    print(dates)
    # normalise and split dataset
    df_train, df_val, df_test = split_dataset(dataset, train_ratio=0.8, val_ratio=0.1)
    train_mean = df_train.mean()
    train_std = df_train.std()
    df_train = (df_train - train_mean) / train_std
    df_val = (df_val - train_mean) / train_std
    df_test = (df_test - train_mean) / train_std

    # use 30 days of data to predict next 5 days
    OUT_STEPS = int(days_to_predict)
    input_width = (
        OUT_STEPS * 10
    )  # number of days to use for predicting out_steps days in the future
    multi_window = WindowGenerator(
        input_width=input_width,
        label_width=OUT_STEPS,
        shift=OUT_STEPS,
        train_df=df_train,
        val_df=df_val,
        test_df=df_test,
        label_columns=["Close"],
    )

    feedback_model = FeedBack(units=128, out_steps=OUT_STEPS)
    history = compile_and_fit(feedback_model, multi_window)  # train model
    # /training over
    # start prediction
    data = (dataset - train_mean) / train_std
    data = np.array(data, dtype=np.float32)
    data = data[len(data) - input_width :]
    print(data.shape)
    ds = tf.keras.utils.timeseries_dataset_from_array(
        data=data,
        targets=None,
        sequence_length=input_width,
        sequence_stride=1,
        shuffle=False,
        batch_size=1,
    )
    prediction = feedback_model.predict(ds)
    results = [p * train_std + train_mean for p in prediction.flatten()]
    results = [r[0] for r in results]
    print(results)
    traces = [
        {"x": dates, "y": results, "name": stock_ticker + " predictions"},
        {
            "x": dataset.index[len(dataset) - input_width - 1 :],
            "y": dataset["Close"][len(dataset) - input_width - 1 :],
            "name": stock_ticker,
        },
    ]

    fig = {
        "data": traces,
        "layout": {
            "title": "{}-day-prediction for {} ".format(
                str(days_to_predict), stock_ticker
            )
        },
    }
    return fig


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
    app.run_server(debug=True)
