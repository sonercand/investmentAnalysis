from re import S
from click import style
from dash import dash, dcc, html, Input, Output, State, callback, callback_context
from pages import navigation
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
from multiprocessing import Pool, Process, Manager
import multiprocessing as mp
from Calculations.portfolioOptimisation import OptimisePortfolio

color1 = "#4990C2"
with open("./data/sector_map.json", "r") as fp:
    sectors = json.load(fp)
options = []
m = 0
for k, v in sectors.items():
    m += 1
    options.append({"label": k, "value": v})
# Modal Pages --------------
## First Page:
firstPage = html.Div(
    [
        dbc.Toast(
            [
                dbc.Row(
                    [
                        dbc.RadioItems(
                            id="goalValues",
                            options=[
                                {
                                    "label": "Suplement Retirement funds I already have",
                                    "value": 1,
                                },
                                {
                                    "label": "For my child's university education.",
                                    "value": 2,
                                },
                                {"label": "For a big purchase.", "value": 3},
                                {"label": "To buy a new car", "value": 4},
                                {"label": "For a house", "value": 5},
                                {
                                    "label": "For protection against inflation.",
                                    "value": 6,
                                },
                                {"label": "For overseas vacation.", "value": 7},
                                {
                                    "label": "No specific reason at the moment.",
                                    "value": 8,
                                },
                            ],
                            labelCheckedClassName="text-success",
                            inputCheckedClassName="border border-success bg-success",
                        ),
                    ],
                    style={"margin": "0 auto", "padding": "2em"},
                ),
            ],
            header="Why do you want to save your money?",
            style={"width": "100%", "padding": "2em"},
        ),
        dbc.Button(
            "",
            color="primary",
            id="goalButton",
            n_clicks=0,
            value="0",
            className="me-12 fa-solid fa-angle-right",
        ),
        dbc.Progress(value=25, id="Progress"),
    ],
    id="firstPage",
)

## 2nd Page
secondPage = [
    html.Div(
        [
            dbc.Toast(
                [
                    dbc.Row(
                        [
                            dcc.Slider(
                                1,
                                50,
                                1,
                                value=5,
                                id="numofYearsToInvest",
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                            ),
                        ],
                        style={"margin": "0 auto", "padding": "2em"},
                    ),
                ],
                header="How long do you intent to invest?",
                style={"width": "100%", "padding": "2em"},
            ),
            dbc.Button(
                "",
                color="primary",
                id="durationBack",
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-left",
            ),
            dbc.Button(
                "",
                color="primary",
                id="durationNext",
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-right",
            ),
            dbc.Progress(value=50, id="Progress"),
        ],
        id="secondPage",
    )
]

thirdPage = [
    html.Div(
        [
            dbc.Toast(
                [
                    dbc.Row(
                        [
                            html.P(
                                "Suggested portfolio risk range is Moderate (0.2-0.5)"
                            ),
                            dcc.RangeSlider(
                                0,
                                1,
                                0.1,
                                value=[0.2, 0.5],
                                id="riskSlider",
                                marks=None,
                                persistence=True,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                            ),
                        ],
                        style={"margin": "0 auto", "padding": "2em"},
                    ),
                    dbc.Row(
                        [
                            html.P(
                                "Please select average ESG score for the portfolio. '1' is the lowest score whereas '7' is the maximum score. "
                            ),
                            dcc.Slider(
                                1,
                                7,
                                0.1,
                                value=5,
                                id="esgSlider",
                                marks=None,
                                persistence=True,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": True,
                                },
                            ),
                        ]
                    ),
                ],
                header="Last questions - Portfolio Tuning",
                style={"width": "100%", "padding": "2em"},
            ),
            dbc.Button(
                "",
                color="primary",
                id="durationBack2",
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-left",
            ),
            dbc.Button(
                "",
                color="primary",
                id="durationNext2",
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-right",
            ),
            dbc.Progress(value=75, id="Progress"),
        ],
        id="thirdPage",
    )
]
pageFour = [
    html.Div(
        [
            dbc.Toast(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.P("Sectors to include"),
                                    dbc.Checklist(
                                        options=options,
                                        id="sectorSelector",
                                        value=[v],
                                        persistence=True,
                                        switch=True,
                                    ),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.P("Create Portfolio"),
                                    dbc.Button(
                                        "",
                                        class_name="fa-solid fa-gears",
                                        id="optimisePortfolio",
                                        color="white",
                                        style={"font-size": "5em"},
                                    ),
                                ],
                                style={"padding-top": "5em"},
                            ),
                        ],
                        style={"margin": "0 auto", "padding": "2em"},
                    ),
                ],
                header="Last questions - Portfolio Tuning",
                style={"width": "100%", "padding": "2em"},
            ),
            dbc.Button(
                "",
                color="primary",
                id="durationBack3",
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-left",
            ),
            dbc.Progress(value=100, id="Progress"),
        ],
        id="forthPage",
    )
]
pagePortfolio = [html.H2("The Optimum Portfolio")]
layout = html.Div(
    [
        dcc.Store(id="memory-riskSlider"),
        dcc.Store(id="memory-esgSlider"),
        navigation.navbar,
        html.Div(
            [
                dbc.Button(
                    "Start New Portfolio",
                    id="start",
                    n_clicks=0,
                    class_name="fa-solid fa-circle-play",
                    color=color1,
                ),
            ],
            style={"margin": "0 auto", "padding": "10em"},
        ),
        dbc.Modal(
            [firstPage],
            id="modal",
            size="lg",
            is_open=False,
        ),
    ],
    id="body",
)
# save user selected values to memory output
@callback(Output("memory-riskSlider", "data"), Input("riskSlider", "value"))
def store_risk(value):

    return value


@callback(Output("memory-esgSlider", "data"), Input("esgSlider", "value"))
def store_esgScore(value):

    return value


@callback(
    Output("body", "children"),
    Input("optimisePortfolio", "n_clicks"),
    [
        State("sectorSelector", "value"),
        State("memory-riskSlider", "data"),
        State("memory-esgSlider", "data"),
    ],
)
def optimise(n_clicks, sectors, risk, esgScore):
    if n_clicks > 0:
        useLogReturns = False
        objFun = "Sharpe"
        data = pd.read_csv("./data/snpFtseClose.csv")
        esgData = pd.read_csv("./data/esgScores_aligned.csv")
        stocks = [item for sublist in sectors for item in sublist]
        stocks = set(stocks)
        stocks = list(stocks)
        esgData = esgData[stocks]
        stocks.append("Date")
        data = data[stocks]
        op = OptimisePortfolio(
            data=data,
            period=5,
            risk=risk,
            objectFunction=objFun,
            useLogReturns=useLogReturns,
        )
        dr, tickers, covMatrix = op.processData()
        expectedAnnualReturns = op.expectedAnnualReturns(dr)
        optWeightsS = op.maximizePortfolioReturns(
            covMatrix,
            tickers,
            expectedAnnualReturns,
            dr,
            esgScore=esgScore,
            esgData=esgData,
        )
        prS = op.portfolioReturns(optWeightsS, expectedAnnualReturns)
        pRiskS = op.portfolioRisk(optWeightsS, covMatrix)
        list_ = list(zip(tickers, optWeightsS.round(7)))

        def take2(element):
            return element[1]

        list_.sort(key=take2, reverse=True)
        table_header = [html.Thead(html.Tr([html.Th("Stock"), html.Th("Weight")]))]
        rows = []
        for s, w in list_:
            rows.append(html.Tr([html.Td(s), html.Td(str(w))]))

        table_body = [html.Tbody(rows)]
        table = dbc.Table(table_header + table_body, bordered=True)
        esgScoreC = op.portfolioESGscore(weights=optWeightsS, esgData=esgData)
        esgResult = html.P("ESG SCORE : {}".format(esgScoreC))
        selectedValues = html.P("risk:{}, esgScore:{}".format(risk, esgScore))
        output = dbc.Row([selectedValues, esgResult, dbc.Col([table])])
        return output
        return [html.P("Optimise for {}, {},{}".format(sectors, risk, esgScore))]


@callback(
    [Output("firstPage", "children")],
    [Input("goalButton", "n_clicks")],
)
def firstToSecond(n_clicks):
    if n_clicks > 0:

        return [secondPage]


@callback(
    [Output("secondPage", "children")],
    [Input("durationBack", "n_clicks"), Input("durationNext", "n_clicks")],
)
def fromSecondPage(n_clicksback, n_clicknext):
    if n_clicksback > 0:

        return [firstPage]
    elif n_clicknext > 0:
        return [thirdPage]


@callback(
    [Output("thirdPage", "children")],
    [Input("durationBack2", "n_clicks"), Input("durationNext2", "n_clicks")],
)
def fromThirdPage(n_clicksback, n_clicknext):
    if n_clicksback > 0:

        return [secondPage]
    elif n_clicknext > 0:
        return [pageFour]


@callback(
    [Output("forthPage", "children")],
    [Input("durationBack3", "n_clicks")],
)
def fromFourthPage(n_clicksback):
    if n_clicksback > 0:

        return [thirdPage]


@callback(
    Output("modal", "is_open"),
    Input("start", "n_clicks"),
    State("start", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open
