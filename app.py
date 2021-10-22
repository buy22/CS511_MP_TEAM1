from dash import Dash, dcc, html, Input, Output, State, dash_table
from Mysql import Mysql
from mongoDB import MongoDB
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
import json

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
        dash_table.DataTable(
            id='live_update_table',
            style_cell={'textAlign': 'left', 'overflow': 'hidden', 'maxWidth': 0, 'textOverflow': 'ellipsis'},
            style_table={'height': '300px', 'overflowY': 'auto'},
            data=[],
            css=[{
                    'selector': '.dash-spreadsheet td div',
                    'rule': '''
                        line-height: 15px;
                        max-height: 30px; min-height: 30px; height: 30px;
                        display: block;
                        overflow-y: hidden;
                    '''
                }],
        ),
        html.Div(id='click_data', style={'whiteSpace': 'pre-wrap', 'height': 200}),
    ])
])

'''
    dcc.Interval(
        id='interval-component',
        interval=3*1000,  # in milliseconds
        n_intervals=0
    )
'''

@app.callback(
    [Output('live_update_table', 'data'),
     Output('live_update_table', 'columns')],
    Input('dropdown1', 'value'),
<<<<<<< HEAD
    Input('interval-component', 'n_intervals'))
def update_figure_table(value, n_intervals):
    if value == "MySQL":
        db = MongoDB('mp_team1', 'test_table1')
=======
    #Input('interval-component', 'n_intervals')
    )
def update_figure_table(value): # , n_intervals
    if value == "Mysql":
        db = MongoDB('mp_team1', 'comments')
>>>>>>> 41013fc3181fdae86be84f34ec175733da08035d
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]
    elif value == "MongoDB":
        db = MongoDB('mp_team1', 'comments')
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]
    else:
        return '3'


@app.callback(
    Output('click_data', 'children'),
    [Input('live_update_table', 'active_cell')],
    [State('live_update_table', 'data')]
)
def display_click_data(active_cell, table_data):
    if active_cell:
        cell = json.dumps(active_cell, indent=2)
        row = active_cell['row']
        col = active_cell['column_id']
        value = table_data[row][col]
        out = '%s' % value
    else:
        out = 'no cell selected'
    return out


@app.callback(
    Output('query_result', 'children'),
    Input('submit_query', 'n_clicks'),
    State('custom_query', 'value'))
def execute_query(n_clicks, value):
    return value

'''
def create_table(dff):
    g = go.Figure(data=[go.Table(
        header=dict(values=['author', 'controversiality',
                            'created_utc', 'distinguished', 'retrieved_on', 'score', 'subreddit', 'body'],
                    fill_color='paleturquoise',
                    align='center'),
        cells=dict(values=[dff.author, dff.controversiality, dff.created_utc, dff.distinguished, dff.retrieved_on,
                           dff.score, dff.subreddit, dff.body],
                   fill_color='lavender',
                   align='left'))
    ])
    #g = ff.create_table(dff)
    return g
'''

if __name__ == '__main__':
    app.run_server(debug=True)
