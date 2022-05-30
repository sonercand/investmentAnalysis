from turtle import back
from dash import dash, dcc, html, Input, Output, State, callback, callback_context
from pages import navigation
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from Calculations.portfolioOptimisation import OptimisePortfolio
import json

# styling params ##############################################
color1 = "#4990C2"
color2 = "rgb(36, 229, 181)"
# Options for sector exclusions ###############################
with open("./data/sector_map.json", "r") as fp:
    sectors = json.load(fp)
options = [{"label": k, "value": v} for k, v in sectors.items()]
# Modal Pages function #########################################
def modalPage(
    modalHeader,
    pageId,
    progressValue,
    inputHtml,
    backButtonId=None,
    forwardButtonId=None,
):
    backButton = ""
    forwardButton = ""
    if backButtonId != None:
        backButton = (
            dbc.Button(
                "",
                color="primary",
                id=backButtonId,
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-left",
            ),
        )

    if forwardButtonId != None:
        forwardButton = (
            dbc.Button(
                "",
                color="primary",
                id=forwardButtonId,
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-right",
            ),
        )
    return html.Div(
        [
            dbc.Toast(
                [
                    dbc.Row(
                        inputHtml,
                        style={"margin": "0 auto", "padding": "2em"},
                    )
                ],
                header=modalHeader,
                style={"width": "100%", "padding": "2em"},
            ),
            dbc.Button(
                "",
                color="primary",
                id=backButtonId,
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-left",
            ),
            dbc.Button(
                "",
                color="primary",
                id=forwardButtonId,
                n_clicks=0,
                value="0",
                className="me-12 fa-solid fa-angle-right",
            ),
            dbc.Progress(value=progressValue, id="Progress", color=color2),
        ],
        id=pageId,
    )


## PAGE 1 #############
page1Html = [
    html.P("Why do you want to save?"),
    html.Br(),
    dbc.RadioItems(
        id="p1Inputs1",
        options=[
            {
                "label": "Suplement Retirement funds I already have",
                "value": 1,
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
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.P("Amount you want to save:"),
    dcc.Input(id="p1Inputs2", type="number", placeholder="GBP", min=1000),
]
modalPage1 = modalPage(
    modalHeader="Purpose of your investment",
    pageId="page1",
    progressValue="0",
    inputHtml=page1Html,
    backButtonId="None",
    forwardButtonId="f1",
)
## Page 2 #############
page2Html = [
    html.P("Number of year planning to hold your savings to grow."),
    dcc.Slider(
        0,
        50,
        5,
        value=5,
        id="p2Inputs1",
        marks=None,
        tooltip={
            "placement": "bottom",
            "always_visible": True,
        },
    ),
    html.P("Target Amount: "),
    dcc.Input(id="p2Inputs2", type="number", placeholder="GBP", min=1000),
]

modalPage2 = modalPage(
    modalHeader="Duration of the Investment",
    pageId="page2",
    inputHtml=page2Html,
    backButtonId="b2",
    forwardButtonId="f2",
    progressValue=20,
)
## Page3 ##################
page3Html = [
    html.P("Up to what percentage of your yearly income are you investing?"),
    dcc.Slider(
        0,
        100,
        25,
        value=25,
        id="p3Inputs1",
        marks=None,
        persistence=True,
        tooltip={
            "placement": "bottom",
            "always_visible": True,
        },
    ),
    html.P(
        " what percentage of returns would you consider fair enough (more would be better but I can live with) for the first year? "
    ),
    dcc.Slider(
        0,
        100,
        5,
        value=5,
        id="p3Inputs2",
        marks=None,
        persistence=True,
        tooltip={
            "placement": "bottom",
            "always_visible": True,
        },
    ),
    html.P(
        "Up to what percentage of loss would you consider acceptable (amouth that would not affect your life style and your current spending profile) based on the returns you are expecting? "
    ),
    dcc.Slider(
        0,
        100,
        5,
        value=5,
        id="p3Inputs3",
        marks=None,
        persistence=True,
        tooltip={
            "placement": "bottom",
            "always_visible": True,
        },
    ),
]
modalPage3 = modalPage(
    modalHeader="Risk Appetite",
    pageId="page3",
    inputHtml=page3Html,
    backButtonId="b3",
    forwardButtonId="f3",
    progressValue=40,
)

## layout ############
layout = html.Div(
    [
        dcc.Store(id="memory-riskSlider"),
        dcc.Store(id="memory-esgSlider"),
        navigation.navbar,
        html.Div(
            [
                dbc.Button(
                    "Create a  New Portfolio",
                    id="start",
                    n_clicks=0,
                    color=color1,
                    style={
                        "background-color": color1,
                        "fontSize": "2em",
                        "color": "white",
                    },
                ),
            ],
            style={"margin": "0 auto", "padding": "15em", "textAlign": "center"},
        ),
        dbc.Modal(
            [modalPage3],
            id="modal",
            size="lg",
            is_open=False,
        ),
    ],
    id="body",
)
