from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from Calculations.calcVolatility import calculateVolatility


color1 = "#4990C2"


def createPredictionsWidget(tic, n_clicks, days_to_predict, id):
    from widgetFunctions import trainAndPredict

    results, dataset, stock_ticker, dates, input_width = trainAndPredict(
        tic, days_to_predict
    )
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


def createVolatilityWidget(tic):
    vol, norm_returns = calculateVolatility(tic)
    widget = dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.ListGroup(
                                        [
                                            dbc.ListGroupItem("Stock: {}".format(tic)),
                                            dbc.ListGroupItem(
                                                "Standard Deviation on Returns: {}".format(
                                                    vol
                                                )
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ],
                width=2,
            ),
            dbc.Col(
                [
                    dcc.Graph(
                        id="graphVolatility",
                        figure={
                            "data": [
                                {
                                    "x": norm_returns.index,
                                    "y": norm_returns["returns_norm"],
                                    "name": tic,
                                }
                            ],
                            "layout": {
                                "title": "Normalised Daily Returns for {}".format(tic)
                            },
                        },
                        style={"marginTop": "4em"},
                    )
                ],
                width=10,
            ),
        ],
        id="volatility",
    )
    return widget


def createCompanyInfoWidget(
    imageSource, companyName, exchange, industry, mCapitalisation, ipo, id="companyInfo"
):
    widget = html.Div(
        dbc.Card(
            [
                dbc.CardImg(src="{}".format(imageSource), top=True),
                dbc.CardBody(
                    [
                        dbc.ListGroup(
                            [
                                dbc.ListGroupItem("Name: {}".format(companyName)),
                                dbc.ListGroupItem("Exchange: {}".format(exchange)),
                                dbc.ListGroupItem("Industry: {}".format(industry)),
                                dbc.ListGroupItem(
                                    "Market Capitalisation: {}".format(mCapitalisation)
                                ),
                                dbc.ListGroupItem("IPO: {}".format(ipo)),
                            ],
                        ),
                    ]
                ),
            ],
        ),
        id=id,
    )
    return widget


def createStockPricePlot(df, tic, id="stockPriceGraph"):
    stockPriceGraph = html.Div(
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
                "layout": {"title": "Stock Prices for {}".format(tic)},
            },
            style={"marginTop": "4em"},
        ),
        id=id,
    )
    return stockPriceGraph


def createStockVsMarketWidget(beta, expectedReturn, id="stockVsMarketVidget"):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.ListGroup(
                        [
                            dbc.ListGroupItem("Beta: {}".format(beta)),
                            dbc.ListGroupItem("CAPM: {}".format(expectedReturn)),
                        ],
                        id=id,
                    ),
                ]
            ),
        ],
        id="stockVsMarketWidget_parent",
    )


def createStockVsMarketGraph(closeDataMarket, closeData, tic, id="stockVsMarketGraph"):
    return html.Div(
        dcc.Graph(
            id="betaGraph",
            figure={
                "data": [
                    go.Scatter(
                        {
                            "x": (
                                (
                                    closeDataMarket["Close"]
                                    - closeDataMarket["Close"].mean()
                                )
                                / closeDataMarket["Close"].std()
                            ),
                            "type": "scatter",
                            "y": (closeData["Close"] - closeData["Close"].mean())
                            / closeData["Close"].std(),
                            "type": "scatter",
                            "name": tic,
                            "mode": "markers",
                        }
                    )
                ],
                "layout": {
                    "title": "Stock vs Market",
                    "xaxis": {"title": "Market"},
                    "yaxis": {"title": "Stock"},
                },
            },
            style={"marginTop": "4em"},
        ),
        id=id,
    )


def createStockSelectionWidget(stocks, tic, id="stock_picker"):
    return dbc.Col(
        [
            dcc.Dropdown(
                id=id,
                options=stocks,
                value=tic,
                multi=False,
                style={"padding": "1em"},
            )
        ],
        id="stock_picker_parent",
        width=12,
    )


def createMarketSelectionWidget(exchangeOptions, defaultExchange, id="market_picker"):
    return dbc.Col(
        [
            dcc.Dropdown(
                id=id,
                options=exchangeOptions,
                value=defaultExchange,
                multi=False,
                style={"padding": "1em"},
            )
        ],
        width=12,
    )


def createSustainabilityWidget(smi, tic, id="sus"):
    susData = smi.getESGData(tic=tic)

    try:
        len(susData)
        table_header = [html.Thead(html.Tr([html.Th("Indicator"), html.Th("Value")]))]
        rows = []
        for key, val in susData.to_dict()["Value"].items():
            if val:
                row = html.Tr([html.Td(key), html.Td(val)])
                rows.append(row)

        table_body = [html.Tbody(rows)]

        table = dbc.Table(table_header + table_body, bordered=True)
        susWidget = html.Div(
            [
                html.H2(
                    "Sustainability Results",
                    style={"color": color1},
                ),
                table,
            ],
            id=id,
            style={"color": "white"},
        )
    except:
        susWidget = html.Div(
            [html.H2("Sustainability Results"), html.Div("No Data Found!")], id=id
        )
    return susWidget
