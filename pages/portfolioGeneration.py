from dash import dash, dcc, html, Input, Output, State, callback, callback_context
from pages import navigation
from Calculations.portfolioOptimisation import OptimisePortfolio
import pandas as pd
import plotly.express as px

lowRisk = [0.0, 0.3]
medRisk = [0.3, 0.7]
highRisk = [0.7, 1.0]
selectedRisk = 0.4
layout = html.Div(
    [
        navigation.navbar,
        html.H2("Risk Apetite"),
        dcc.Slider(
            0,
            1,
            0.1,
            value=selectedRisk,
            id="riskSlider",
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        dcc.Graph(
            id="porfolioRiskReturn",
            figure={},
        ),
    ]
)


@callback(Output("porfolioRiskReturn", "figure"), [Input("riskSlider", "value")])
def displayPortRiskReturn(value):
    riskRange = [0, value]
    data = pd.read_csv("./data/snpFtseClose.csv")
    op = OptimisePortfolio(
        data=data,
        period=3,
        useLogReturns=True,
        workDaysinYear=252,
        objectFunction="Sharpe",
        risk=riskRange,
    )
    dr, tickers, covMatrix = op.processData()
    expAR = op.expectedAnnualReturns(dr)
    weights = op.maximizePortfolioReturns(
        covMatrix=covMatrix, tickers=tickers, expectedAnnualReturns=expAR
    )
    optimumPortfolioRisk = op.portfolioRisk(weights, covMatrix)
    optimumPortfolioReturn = op.portfolioReturns(weights, expAR)
    generatedPortfolios = op.genRandomPortfolios(
        expAR, covMatrix, tickers, n_iter=10000
    )
    traces = [
        {"x": generatedPortfolios["risk"], "y": generatedPortfolios["returns"]},
        {
            "x": optimumPortfolioRisk,
            "y": optimumPortfolioReturn,
        },
    ]

    figure = (
        {
            "data": traces,
            "layout": {"title": "Potential Portfolio Performance"},
        },
    )
    fig = px.scatter(
        generatedPortfolios,
        x="risk",
        y="returns",
    )
    fig2 = px.scatter(optimumPortfolioRisk, optimumPortfolioReturn)

    return fig
