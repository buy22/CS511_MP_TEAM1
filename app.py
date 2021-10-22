from dash import Dash, dcc, html, Input, Output, State, dash_table
from Mysql import Mysql
from mongoDB import MongoDB
import pandas as pd
import plotly.graph_objects as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Store(id='database'),
    html.Div([
        html.H3('Select your database'),
        dcc.Dropdown(
            id='dropdown1',
            options=[
                {'label': 'MySQL', 'value': 'MySQL'},
                {'label': 'MongoDB', 'value': 'MongoDB'},
                {'label': 'Neo4j', 'value': 'Neo4j'},
            ],
            value='MySQL'
        )
    ]),
    html.Div([
        html.H3('Section 1'),
    ]),
    html.Div([ # TODO/WIP
        html.H3('Section 2: Workflows'),
        html.Table([
            # Header
            html.Thead(
                html.Tr([html.Th("Workflow"),
                        html.Th("Status"),
                        html.Th("Attribute1"),
                        html.Th("Attribute2")])
            ),
            # Body
            html.Tbody([
                html.Tr([html.Td("temp"),
                        html.Td("temp"),
                        html.Td("temp"),
                        html.Td("temp")])
            ])
        ], style={'width': '75%', 'marginLeft':'auto', 'marginRight':'auto'})
    ]),
    html.Div([
        html.H3('Section 3'),
        html.Div(dcc.Textarea(
                    id='custom_query',
                    placeholder='Enter your query here...',
                    style={'width': '80%', 'height': 150},
                ),
                 style=dict(display='flex', justifyContent='center')),
        html.Div(html.Button('Query', id='submit_query', n_clicks=0),
                 style=dict(display='flex', justifyContent='center')),
        html.Div(id='query_result'),
        dcc.Graph(id='live_update_table'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # in milliseconds
            n_intervals=0
        )
    ])
])


@app.callback(
    Output('live_update_table', 'figure'),
    Input('dropdown1', 'value'),
    Input('interval-component', 'n_intervals'))
def update_figure_table(value, n_intervals):
    if value == "MySQL":
        db = MongoDB('mp_team1', 'test_table1')
        df = db.all_data()
        d = df.to_json(orient="split")
        fig = create_table(df)
        return fig
    elif value == "MongoDB":
        db = MongoDB('mp_team1', 'test_table1')
        df = db.all_data()
        d = df.to_json(orient="split")
        fig = create_table(df)
        return fig
    else:
        return '3'


@app.callback(
    Output('query_result', 'children'),
    Input('submit_query', 'n_clicks'),
    State('custom_query', 'value'))
def execute_query(n_clicks, value):
    return value


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
