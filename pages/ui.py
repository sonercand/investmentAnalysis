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
        persistence=True,
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
        persistence=True,
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
        "Up to what percentage of loss would you consider acceptable (amounth that would not affect your life style and your current spending profile) based on the returns you are expecting? "
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
## Page4 #####
page4Html = [
    html.P(
        "Please specify the average esg score for the portfolio you want us to build. The Score values are between 1 and 7 where 1 is the lowest score any company can get in terms of their esg practices whereas 7 signifies the highest positive impact on the environment. "
    ),
    dcc.Slider(
        1,
        7,
        0.1,
        value=5,
        id="p4Inputs1",
        marks=None,
        persistence=True,
        tooltip={
            "placement": "bottom",
            "always_visible": True,
        },
    ),
]
modalPage4 = modalPage(
    modalHeader="Environment and Impact of your Savings and Risk",
    pageId="page4",
    inputHtml=page4Html,
    backButtonId="b4",
    forwardButtonId="f4",
    progressValue=60,
)

### page5 ####
page5Html = [
    html.P("Base on your answers so far, suggested risk range for you is:"),
    dcc.RangeSlider(
        0,
        1,
        0.1,
        value=[0.1, 0.3],
        marks={
            0.1: "Low Risk",
            0.3: "Moderate Risk",
            0.5: "High Risk",
            0.7: "Very High Risk",
            0.9: "Extreme",
        },
        id="p5Inputs1",
        persistence=True,
        tooltip={
            "placement": "top",
            "always_visible": True,
        },
    ),
    html.P(id="investmentAmount"),
    html.P(id="howLong"),
    html.P(id="targetAmount"),
    html.P(id="riskRange"),
    html.P(id="esgScore"),
]
modalPage5 = modalPage(
    modalHeader="Summary",
    pageId="page5",
    inputHtml=page5Html,
    backButtonId="b5",
    forwardButtonId="f5",
    progressValue=80,
)

## layout ############
layout = html.Div(
    [
        dcc.Store(id="memory-p1Inputs1"),
        dcc.Store(id="memory-p1Inputs2"),
        dcc.Store(id="memory-p2Inputs1"),
        dcc.Store(id="memory-p2Inputs2"),
        dcc.Store(id="memory-p3Inputs1"),
        dcc.Store(id="memory-p3Inputs2"),
        dcc.Store(id="memory-p3Inputs3"),
        dcc.Store(id="memory-p4Inputs1"),
        dcc.Store(id="memory-p5Inputs1"),
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
            [modalPage1],
            id="modal",
            size="lg",
            is_open=False,
        ),
    ],
    id="body",
)
inputs_ = [
    "p1Inputs1",
    "p1Inputs2",
    "p2Inputs1",
    "p2Inputs2",
    "p3Inputs1",
    "p3Inputs2",
    "p3Inputs3",
    "p4Inputs1",
    "p5Inputs1",
]
# persist values
for input_ in inputs_:

    @callback(Output("memory-{}".format(input_), "data"), Input(input_, "value"))
    def store_risk(value):
        return value


page = [modalPage1, modalPage2, modalPage3, modalPage4, modalPage5]
# f1 -> modalPage2
# f2 -> modalPage3
@callback(
    [Output("firstPage", "children")],
    [Input("goalButton", "n_clicks")],
)
def firstToSecond(n_clicks):
    if n_clicks > 0:

        return [secondPage]
