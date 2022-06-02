import dash_bootstrap_components as dbc

color1 = "#4990C2"
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Stock Analysis", href="/stock-analysis")),
        dbc.NavItem(dbc.NavLink("Portfolio Analysis", href="/portfolio-analysis")),
        dbc.NavItem(dbc.NavLink("Portfolio Generation", href="/portfolio-generation")),
        dbc.NavItem(dbc.NavLink("UI Test", href="/uitest")),
        dbc.NavItem(dbc.NavLink("CAPM", href="/capm")),
        dbc.NavItem(dbc.NavLink("Smart Beta", href="/beta")),
    ],
    brand="PortAI",
    brand_href="/",
    color=color1,
    dark=True,
)
