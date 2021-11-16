from Mysql import Mysql
from Neo4j import Neo4j
from mongoDB import MongoDB
from dash import Dash, dcc, html, Input, Output, State, dash_table
from app import app, server
import pandas as pd
import json

from subcomponent import Subcomponent

subcomponents = []

layout = html.Div([
    # select database
    html.Div([
        html.H3('Select your database'),
        dcc.Dropdown(
            id='dropdown_subcomponent',
            options=[
                {'label': 'MySQL', 'value': 'MySQL'},
                {'label': 'MongoDB', 'value': 'MongoDB'},
                {'label': 'Neo4j', 'value': 'Neo4j'},
            ],
            style={'width': '50%'},
            value='Neo4j'
        )
    ]),
    # create subcomponents
    html.Div([
        html.H3('Create Subcomponents for subcomponents'),
        html.Div(dcc.Dropdown(
            id='attributes_subcomponent',
            options=[],
            value=[], placeholder='select attributes to keep',
            multi=True
        ), style={'height': 50}),
        html.Div(dcc.Input(id='subcomponent_name', placeholder="name of the subcomponent"),
                 style={'height': 30, 'margin-right': 10}),
        html.Br(),
        html.Div(dcc.Input(id='condition1', type='number', placeholder="score greater than?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(dcc.Input(id='condition2', type='number', placeholder="controversiality (0 or 1)"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(dcc.Input(id='condition3', placeholder="which author?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(dcc.Input(id='condition4', placeholder="what keyword to search?"),
                 style={'display': 'flex', 'float': 'left', 'height': 30, 'margin-right': 10}),
        html.Div(html.Button('Create Subcomponent', id='create_subcomponent', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white'}),
                 style={'margin-top': 50, 'height': 50}),
        html.Div(id='create_subcomponent_result',
                 style={'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
    ]),
    # subcomponent table
    html.Div([
        html.H3('Subcomponents Table'),
        dash_table.DataTable(
            id='subcomponent_table',
            columns=[
                {'name': 'ID', 'id': 'subcomponent_table_id'},
                {'name': 'Database', 'id': 'subcomponent_table_db'},
                {'name': 'Name', 'id': 'subcomponent_table_name'},
                {'name': 'Score Greater Than', 'id': 'subcomponent_table_score'},
                {'name': 'Controversiality Less Than', 'id': 'subcomponent_table_controversiality'},
                {'name': 'Author', 'id': 'subcomponent_table_author'},
                {'name': 'Search Words', 'id': 'subcomponent_table_search'},
            ],
            data=[],
            style_cell={'textAlign': 'left', 'overflow': 'hidden', 'maxWidth': 0, 'textOverflow': 'ellipsis'},
            style_table={'overflowY': 'show'},
            page_current=0,
            page_size=10,
        ),
        html.Div(id='subcomponent_click_data', style={'whiteSpace': 'pre-wrap'}),
    ])
])


@app.callback(
    Output('attributes_subcomponent', 'options'),
    Input('dropdown_subcomponent', 'value'))
def get_columns(value):
    db, df = None, None
    if value == "MySQL":
        db = Mysql('team1', 'reddit_data')
    elif value == "MongoDB":
        db = MongoDB('mp_team1', 'comments')
    else:
        db = Neo4j('neo4j')
    df = db.all_data()
    cols = df.columns
    return [{'label': opt, 'value': opt} for opt in cols]


@app.callback(
    Output('create_subcomponent_result', 'children'),
    Input('create_subcomponent', 'n_clicks'),
    [State('condition1', 'value'),
     State('condition2', 'value'),
     State('condition3', 'value'),
     State('condition4', 'value'),
     State('subcomponent_name', 'value'),
     State('attributes_subcomponent', 'value'),
     State('dropdown_subcomponent', 'value')]
)
def create_subcomponent(n_clicks, condition1, condition2, condition3, condition4,
                        subcomponent_name, attributes, db):
    if n_clicks:
        if condition2 is not None and (int(condition2) < 0 or int(condition2) > 1):
            return "Invalid controversiality"
        s = Subcomponent(db, len(subcomponents), subcomponent_name,
                         [condition1, condition2, condition3, condition4], attributes)
        subcomponents.append(s)
        return ""


@app.callback(
    [Output('subcomponent_table', 'data'),
     Output('subcomponent_table', 'columns')],
    [Input('create_subcomponent', 'n_clicks')])
def update_subcomponent_table(n_clicks):
    to_add = []
    for subcomponent in subcomponents:
        to_add.append(subcomponent.to_list())
    columns = ['ID', 'Database', 'Name', 'Attributes', 'Score Greater Than',
               'Controversiality Less Than', 'Author', 'Search Words']
    df = pd.DataFrame(to_add, columns=columns)
    return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]


@app.callback(
    Output('subcomponent_click_data', 'children'),
    Input('subcomponent_table', 'active_cell'),
    State('subcomponent_table', 'data'))
def subcomponent_click_data(active_cell, table_data):
    if active_cell:
        cell = json.dumps(active_cell, indent=2)
        row = active_cell['row']
        col = active_cell['column_id']
        value = table_data[row][col]
        out = '%s' % value
    else:
        out = 'no cell selected/no data in the table'
    return out