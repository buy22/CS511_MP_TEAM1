from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from app import app

subcomponents = [1,2,3,4]


layout = html.Div([
    html.H1('General Product Sales', style={"textAlign": "center"}),
    dcc.Graph(id='my-map', figure={}),
])