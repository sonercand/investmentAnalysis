from turtle import back, bgcolor
from dash import dash, dcc, html, Input, Output, State, callback, callback_context
from matplotlib.pyplot import fill, text
from pages import navigation
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from Calculations.portfolioOptimisation import OptimisePortfolio
import json
import numpy as np
import yfinance as yf

# styling params ##############################################
color1 = "#4990C2"
color2 = "rgb(36, 229, 181)"
# Options for sector exclusions ###############################
with open("./data/sector_map.json", "r") as fp:
    sectors = json.load(fp)
options = []
m = 0
for k, v in sectors.items():
    m += 1
    options.append({"label": k, "value": v})
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
    html.P("Number of years planning to hold your savings to grow."),
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
    html.P("Please Toggle to include or exclude sectors."),
    dbc.Checklist(
        options=options,
        id="p4Inputs2",
        value=[v],
        persistence=True,
        switch=True,
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
    dbc.Button(
        "Display Summary",
        color=color1,
        id="summaryButton",
        n_clicks=0,
        value="0",
    ),
    html.P(id="Summary"),
]
modalPage5 = modalPage(
    modalHeader="Summary",
    pageId="page5",
    inputHtml=page5Html,
    backButtonId="b5",
    forwardButtonId="None",
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
        dcc.Store(id="memory-p4Inputs2"),
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
    "p4Inputs2",
    "p5Inputs1",
]
# persist values##############
def persistDat(memory_, input_):
    @callback(Output(memory_, "data"), Input(input_, "value"))
    def store1(value):
        return value


for input_ in inputs_:
    persistDat("memory-{}".format(input_), input_)


### MODAL PAGE CONTROLS ########################################
pages = [modalPage1, modalPage2, modalPage3, modalPage4, modalPage5]
ms = [1, 2, 3, 4, 5]
# Modal Page Arrow control


def modalArrowControls(number, pages):
    inputs = []
    if number != 1:
        inputs.append(Input("b{}".format(number), "n_clicks"))
    if number != 5:
        inputs.append(Input("f{}".format(number), "n_clicks"))

    @callback([Output("page{}".format(number), "children")], inputs)
    def forwardModal(*args):
        if number == 1:
            n_clicksf = args[0]
            n_clicksb = 0
        if number == 5:
            n_clicksb = args[0]
            n_clicksf = 0
        elif number > 1:
            n_clicksb = args[0]
            n_clicksf = args[1]
        if n_clicksb > 0:
            nextPage = pages[number - 2]
            return [nextPage]
        if n_clicksf > 0:
            nextPage = pages[number]
            return [nextPage]


for number in [1, 2, 3, 4, 5]:
    modalArrowControls(number, pages)

## Update Summary Page
@callback(
    [Output("Summary", "children")],
    [Input("summaryButton", "n_clicks")],
    [
        State("memory-p1Inputs2", "data"),
        State("memory-p2Inputs1", "data"),
        State("memory-p2Inputs2", "data"),
        State("memory-p5Inputs1", "data"),
        State("memory-p4Inputs1", "data"),
    ],
)
def updateSummary(
    n_clicks, investmentAmount, howLong, targetAmount, riskRange, esgScore
):
    if n_clicks > 0:
        output = dbc.Col(
            html.Div(
                [
                    html.H4("Summary"),
                    html.Hr(),
                    html.P(
                        "Amount to be invested {} GBP.".format(investmentAmount),
                    ),
                    html.P(
                        "Target amount is {} after {} years.".format(
                            targetAmount, howLong
                        )
                    ),
                    html.P("Selected risk range {}.".format(riskRange)),
                    html.P("Selected ESG score {} or higher".format(esgScore)),
                    html.Br(),
                    dbc.Button(
                        "Create Portfolio",
                        color="secondary",
                        outline=True,
                        id="createPortfolio",
                    ),
                ],
            ),
            md=12,
        )

        return [output]


## GENERATE PORTFOLIO##########
@callback(
    Output("body", "children"),
    Input("createPortfolio", "n_clicks"),
    [
        State("memory-p1Inputs2", "data"),
        State("memory-p2Inputs1", "data"),
        State("memory-p2Inputs2", "data"),
        State("memory-p5Inputs1", "data"),
        State("memory-p4Inputs1", "data"),
        State("memory-p4Inputs2", "data"),
    ],
)
def optimise(
    n_clicks, investmentAmount, howLong, targetAmount, riskRange, esgScore, sectors
):
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
            risk=riskRange,
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
        # calculate expected returns for the user selected time frame
        expectedReturns = []
        worstReturns = []
        expectedRisks = []
        bestReturns = []
        years = []
        lower_ = []
        higher_ = []
        yearEndAmount = investmentAmount
        worstAmount = investmentAmount
        bestAmount = investmentAmount
        for y_ in range(howLong + 1):
            years.append(y_)
            lower_.append(investmentAmount)
            higher_.append(targetAmount)
            expectedReturns.append(yearEndAmount)
            worstReturns.append(worstAmount)
            bestReturns.append(bestAmount)
            yearEndAmount = (prS + 1) * yearEndAmount
            worstAmount = (prS + 1 - pRiskS) * worstAmount
            bestAmount = (
                prS + 1 + pRiskS / 2
            ) * bestAmount  # it explodes exponantially
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=years,
                y=expectedReturns,
                fill="tozeroy",
                mode="lines+markers",
                line_color="blue",
                fillcolor="rgba(171, 226, 251,0.3)",
                name="Expected Saving Amount",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=years,
                y=worstReturns,
                fill="tozeroy",
                mode="lines+markers",
                line_color="rgba(242, 75, 108,1)",
                fillcolor="rgba(255,255,255,1)",
                name="Worst Case",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=years,
                y=bestReturns,
                fill="tonexty",
                mode="lines+markers",
                line_color="rgba(10, 219, 122,1)",
                fillcolor="rgba(10, 219, 122,0.1)",
                name="Best Possible case",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=years,
                y=lower_,
                line=dict(color="red", width=1, dash="dash"),
                fill=None,
                mode="lines",
                fillcolor="rgba(242, 75, 108,0.3)",
                name="Starting Amount",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=years,
                y=higher_,
                line=dict(color="#333", width=1, dash="dash"),
                fill=None,
                mode="lines",
                name="Target Amount",
            )
        )
        fig.update_layout(
            title="Expected Amount Saved vs Years",
            xaxis_title="Years",
            yaxis_title="Growth(GBP)",
            plot_bgcolor="white",
            hovermode="x unified",
        )
        returnsGraph = dcc.Graph(
            figure=fig,
            id="ports",
            animate=True,
        )
        ### Portfolio Holdings ##########################################
        list_ = list(zip(tickers, optWeightsS.round(7)))

        def take2(element):
            return element[1]

        list_.sort(key=take2, reverse=True)
        table_header = [
            html.Thead(
                html.Tr([html.Th("Stock"), html.Th("Weight"), html.Th("Amount(GBP)")])
            )
        ]
        rows = []
        stockWeightDict = {}
        for s, w in list_:
            if w > 0:
                stockWeightDict[s] = w
                rows.append(
                    html.Tr(
                        [
                            html.Td(s),
                            html.Td(str(w)),
                            html.Td(str((w * investmentAmount).round(2))),
                        ]
                    )
                )
        rows.append(
            html.Tr(
                [
                    html.Td("Sum"),
                    html.Td(np.sum(list(stockWeightDict.values()))),
                    html.Td(investmentAmount),
                ]
            )
        )
        table_body = [html.Tbody(rows)]
        table = dbc.Table(table_header + table_body, bordered=True)
        tableContainer = dbc.Col(
            [html.H2("Portfolio Holdings", id="tableHeader"), table], width=6
        )
        ## Portfolio SUmmary ####################################
        portFolioExpectedReturns = prS
        portFolioExpectedRisk = pRiskS
        esgScoreC = op.portfolioESGscore(weights=optWeightsS, esgData=esgData)
        esgResult = html.P("ESG SCORE : {}".format(esgScoreC))
        portfolioSummary = dbc.Col(
            [
                html.Div(
                    [
                        html.H2("Portfolio Summary", id="portSum"),
                        dbc.Card(
                            dbc.CardBody(
                                "Total Amount to invest: {}".format(investmentAmount)
                            ),
                        ),
                        dbc.Card(
                            "Annual Expected Returns: {}".format(prS.round(2)),
                            body=True,
                        ),
                        dbc.Card(
                            "Annual Expected Portfolio Volatility: {}".format(
                                pRiskS.round(2)
                            ),
                            body=True,
                        ),
                        dbc.Card(
                            "Current ESG Score of the Portfolio: {}".format(
                                esgScoreC.round(2)
                            ),
                            body=True,
                        ),
                    ],
                    id="summaryDiv",
                )
            ],
            width=6,
        )

        # Historical Performances######################
        def transform(df):
            df = (df.pct_change(1) + 1).cumprod()
            df.dropna(inplace=True)
            return df

        # calc portfolios historic cumilative returns
        stocks_and_date = list(stockWeightDict.keys())
        dataPort = op.data[stocks_and_date]
        drPort = dataPort.pct_change(1)
        cum_res = (drPort + 1).cumprod()
        cum_res.dropna(inplace=True)
        array_ = []
        for k, v in stockWeightDict.items():
            ll = np.ones(len(cum_res[k])) * v
            array_.append(cum_res[k] * ll)
        res = pd.concat(array_, axis=1)
        portCumRet = res.sum(axis=1, skipna=True)
        min_date = portCumRet.index.min()
        cum_res = (dataPort[dataPort.index >= min_date].pct_change(1) + 1).cumprod()
        cum_res.dropna(inplace=True)
        array_ = []
        for k, v in stockWeightDict.items():
            ll = np.ones(len(cum_res[k])) * v
            array_.append(cum_res[k] * ll)
        res = pd.concat(array_, axis=1)
        portCumRet = res.sum(axis=1, skipna=True)
        # ftse 100
        print("start FTSE")
        ftseData = yf.download("^FTSE", "2017-05-26", "2022-05-25")
        ftseData = ftseData["Adj Close"]
        ftseData = ftseData[ftseData.index >= min_date]
        ftseCumRet = transform(ftseData)
        # snp500
        print("start SNP")
        snpData = yf.download("^GSPC", "2017-05-26", "2022-05-25")
        snpData = snpData["Adj Close"]
        snpData = snpData[snpData.index >= min_date]
        snpCumRet = transform(snpData)
        print(portCumRet.index.min())
        snpCumRet = snpCumRet[snpCumRet.index >= portCumRet.index.min()]
        print(portCumRet.shape, snpCumRet.shape, ftseCumRet.shape)
        traces = []

        traces.append(
            {
                "x": snpCumRet.index,
                "y": snpCumRet,
                "name": "S&P 500",
                "mode": "lines",
                "line": dict(color="#bfc1c1"),
                "line_color": "rgb(90, 91, 91)",
            }
        )
        traces.append(
            {
                "x": ftseCumRet.index,
                "y": ftseCumRet,
                "name": "FTSE 100",
                "mode": "lines",
                "line": dict(color="#6c7070"),
                "line_color": "rgb(90, 91, 91)",
            }
        )
        traces.append(
            {
                "x": portCumRet.index,
                "y": portCumRet,
                "name": "Selected Portfolio",
                "mode": "lines",
                "line_color": "blue",
            }
        )
        graphHist = dcc.Graph(
            figure={
                "data": traces,
                "layout": {
                    "title": "Historical Performance",
                    "xaxis": {"title": "Date"},
                    "yaxis": {"title": "Returns"},
                },
            },
            id="ports",
            animate=True,
        )
        ## Value At RISK ###################
        drPort = drPort.sum(axis=1, skipna=True).round(3)
        VaRdaily = drPort.quantile(0.01)  # at 99%
        VaRMonthly = VaRdaily * np.sqrt(20)
        VaRYearly = VaRdaily * np.sqrt(252)
        figHistogram = px.histogram(drPort, nbins=100)
        graphHistogram = dcc.Graph(id="histogram", figure=figHistogram, animate=True)
        VaRTable = dbc.Col(
            [
                html.Div(
                    [
                        html.H2("Value At Risk @99%", id="portSum"),
                        dbc.Card(
                            dbc.CardBody("VaR Daily: {}".format(VaRdaily.round(2))),
                        ),
                        dbc.Card(
                            "VaR Monthly: {}".format(VaRMonthly.round(2)),
                            body=True,
                        ),
                        dbc.Card(
                            "VaR Yearly: {}".format(VaRYearly.round(2)),
                            body=True,
                        ),
                    ],
                    id="varDiv",
                )
            ],
            width=6,
        )
        returnGraphContainer = dbc.Col(
            [html.H2("Expected Portfolio Performance", id="returns"), returnsGraph],
            width=6,
        )
        graphHistContainer = dbc.Col(
            [html.H2("Historical Performance", id="history"), graphHist], width=6
        )
        histogramContainer = dbc.Col(
            [
                html.H2("Histogram of Historical Daily Returns", id="history"),
                graphHistogram,
            ],
            width=6,
        )
        output = [
            navigation.navbar,
            dbc.Row(
                [
                    portfolioSummary,
                    returnGraphContainer,
                    html.Br(),
                    VaRTable,
                    histogramContainer,
                    graphHistContainer,
                    tableContainer,
                ]
            ),
        ]
        return output


@callback(
    Output("modal", "is_open"),
    Input("start", "n_clicks"),
    State("start", "is_open"),
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open
