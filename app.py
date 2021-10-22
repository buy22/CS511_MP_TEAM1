from dash import Dash, dcc, html, Input, Output, State, dash_table
from Mysql import Mysql
from mongoDB import MongoDB
import pandas as pd
import plotly.graph_objects as go


app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H3('Select your database'),
        dcc.Dropdown(
            id='dropdown1',
            options=[
                {'label': 'Mysql', 'value': 'Mysql'},
                {'label': 'MongoDB', 'value': 'MongoDB'},
                {'label': 'graph database', 'value': 'graph database'},
            ],
            value='Mysql'
        )
    ]),
    html.Div([
        html.H3('Section 1'),
        html.Div(dcc.Input(id='input-on-submit', type='text')),
        html.Button('Submit', id='submit-val', n_clicks=0),
        html.Div(id='container-button-basic',
                 children='Enter a value and press submit')
    ]),
    html.Div([
        html.H3('Section 2')
    ]),
    html.Div([
        html.H3('Section 3'),
        dcc.Store(id='all_data'),
        html.Div(id='main_data_table'),
        dcc.Graph(id='live_update_graph')
    ])
])


@app.callback(
    Output('main_data_table', 'children'),
    Output('live_update_graph', 'figure'),
    Input('dropdown1', 'value'))
def update_figure_table(value):
    if value == "Mysql":
        return '1'
    elif value == "MongoDB":
        db = MongoDB('mp_team1', 'test_table1')
        df = db.all_data()
        d = df.to_json(orient="split")
        fig = create_table(df)
        return d, fig
    else:
        return '3'


def create_table(dff):
    g = go.Figure(data=[go.Table(
        header=dict(values=list(dff.columns),
                    fill_color='paleturquoise',
                    align='center'),
        cells=dict(values=[dff.x],
                   fill_color='lavender',
                   align='center'))
    ])
    return g


if __name__ == '__main__':
    app.run_server(debug=True)
