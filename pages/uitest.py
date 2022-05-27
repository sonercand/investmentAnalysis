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

color1 = "#4990C2"
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
                        [],
                        style={"margin": "0 auto", "padding": "2em"},
                    ),
                ],
                header="Last questions",
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
            dbc.Progress(value=75, id="Progress"),
        ],
        id="thirdPage",
    )
]
layout = html.Div(
    [
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
    ]
)


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
def firstToSecond(n_clicksback, n_clicknext):
    if n_clicksback > 0:

        return [firstPage]
    elif n_clicknext > 0:
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
