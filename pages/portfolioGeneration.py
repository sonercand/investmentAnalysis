from dash import dash, dcc, html, Input, Output, State, callback, callback_context
from pages import navigation, stock
from Calculations.portfolioOptimisation import OptimisePortfolio
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
from multiprocessing import Pool, Process, Manager
import multiprocessing as mp

"""
1) filter companies by sector
2) optimise by risk portfolio volatility for maximum returns

"""
with open("./data/sector_map.json", "r") as fp:
    sectors = json.load(fp)
options = []
m = 0
for k, v in sectors.items():
    m += 1
    options.append({"label": k, "value": v})
selectedRisk = 0.4
layout = html.Div(
    [
        navigation.navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2("Sectors to Include"),
                                dbc.Checklist(
                                    options=options,
                                    id="sectorSelector",
                                    value=[v],
                                    switch=True,
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                html.H2("Select Portfolio Volatility"),
                                dcc.RangeSlider(
                                    0,
                                    1,
                                    0.1,
                                    value=[0.1, 0.2],
                                    id="riskSlider",
                                    marks=None,
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                ),
                                html.H2("Select ESG Score"),
                                dcc.Slider(
                                    1,
                                    7,
                                    0.1,
                                    value=5,
                                    id="esgSlider",
                                    marks=None,
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                html.H2("Select objective function"),
                                dbc.Select(
                                    id="objfunction",
                                    options=[
                                        {"label": "Sharpe Ratio", "value": "Sharpe"},
                                        {
                                            "label": "Portfolio Return Rate",
                                            "value": "Returns",
                                        },
                                        {"label": "Sortino Ratio", "value": "Sortino"},
                                    ],
                                ),
                                html.H2("Select Return Calculation Method"),
                                dbc.Select(
                                    id="logReturns",
                                    options=[
                                        {
                                            "label": "Use Log Returns",
                                            "value": "logReturns",
                                        },
                                        {
                                            "label": "Use Percentage Returns",
                                            "value": "pctReturns",
                                        },
                                    ],
                                ),
                            ]
                        ),
                    ]
                ),
                dbc.Button("Set", n_clicks=0, id="setParameters"),
                html.Div(id="graphHolder"),
                html.Div(id="test"),
            ]
        ),
    ]
)


@callback(
    Output("graphHolder", "children"),
    Input("setParameters", "n_clicks"),
    [
        State("sectorSelector", "value"),
        State("riskSlider", "value"),
        State("objfunction", "value"),
        State("logReturns", "value"),
        State("esgSlider", "value"),
    ],
)
def plotGraph(n_clicks, sectors, riskValue, objFun, logReturns, esgScore):
    if n_clicks > 0:
        # riskRange = [0, riskValue]
        if logReturns == "logReturns":
            useLogReturns = True
        else:
            useLogReturns = False
        data = pd.read_csv("./data/snpFtseClose.csv")
        print("columns of the original data: {}".format(data.columns))
        esgData = pd.read_csv("./data/esgScores_aligned.csv")
        # sectors = [sectors]
        stocks = [item for sublist in sectors for item in sublist]
        stocks = set(stocks)
        stocks = list(stocks)
        print(stocks)
        esgData = esgData[stocks]
        stocks.append("Date")
        print(stocks)
        data = data[stocks]
        print(data)

        op = OptimisePortfolio(
            data=data,
            period=5,
            risk=riskValue,
            objectFunction=objFun,
            useLogReturns=useLogReturns,
        )
        dr, tickers, covMatrix = op.processData()
        print("this is dr")
        print(dr.head())
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
        returns = []
        risks = []
        """
        for k in range(10):
            riskA = k / 10
            op.useRiskRange = False
            op.risk = riskA
            optWeights = op.maximizePortfolioReturns(
                covMatrix, tickers, expectedAnnualReturns
            )
            pr = op.portfolioReturns(optWeights, expectedAnnualReturns)
            pRisk = op.portfolioRisk(optWeights, covMatrix)
            returns.append(pr)
            risks.append(pRisk)
        
        """
        randomPortfolios = op.genRandomPortfolios(
            expectedAnnualReturns, covMatrix, tickers, 10000
        )
        traces = []
        traces.append(
            {
                "x": randomPortfolios.risk,
                "y": randomPortfolios.returns,
                "name": "Random Portfolios",
                "mode": "markers",
                "colorscale": "Rainbow",
                "opacity": 0.5,
            }
        )
        """traces.append(
            {
                "x": risks,
                "y": returns,
                "name": "Optimum values",
                "color": "green",
                "size": 14,
            }
        )"""
        traces.append(
            {
                "x": [pRiskS],
                "y": [prS],
                "name": "Optimum for the selected range",
                "color": "red",
                "size": 28,
            }
        )
        print(pRiskS, prS)
        graph = dcc.Graph(
            figure={
                "data": traces,
                "layout": {
                    "title": "Risk vs Returns",
                    "xaxis": {"title": "Risk"},
                    "yaxis": {"title": "Returns"},
                },
            },
            id="ports",
            animate=True,
        )
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

        # get portfolio esg score:
        stocks = list(op.data.columns)

        print(esgData)
        esgData = esgData[stocks]
        print(optWeightsS.shape, esgData.shape)
        esgScore = op.portfolioESGscore(weights=optWeightsS, esgData=esgData)
        esgResult = html.P("ESG SCORE : {}".format(esgScore))
        output = dbc.Row([dbc.Col([graph]), esgResult, dbc.Col([table])])
        return output
