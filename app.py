from dash import Dash, dcc, html, Input, Output, callback
from pages import (
    navigation,
    portfolioGeneration,
    # ui,
    # uitest,
    uiCAPM,
)  # , stock, portfolio,uitest
import dash_bootstrap_components as dbc


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
)
server = app.server

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

layout_index = html.Div([navigation.navbar])


@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/stock-analysis":
        return None  # stock.layout
    elif pathname == "/portfolio-analysis":
        return None  # portfolio.layout
    elif pathname == "/":
        return layout_index
    elif pathname == "/portfolio-generation":
        return portfolioGeneration.layout
    elif pathname == "/uitest":
        return None  # ui.layout
    elif pathname == "/capm":
        return uiCAPM.layout
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=False)
