import dash_bootstrap_components as dbc

color1 = "#4990C2"
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Stock Analysis", href="/stock-analysis")),
        dbc.NavItem(dbc.NavLink("Portfolio Analysis", href="/portfolio-analysis")),
    ],
    brand="Port/Stock",
    brand_href="/",
    color=color1,
    dark=True,
)