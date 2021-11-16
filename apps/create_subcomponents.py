from dash import Dash, dcc, html, Input, Output, State, dash_table
from app import app, server

subcomponents = [1,2,3,4]

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
        html.H3('Create Subcomponents for workflows'),
        html.Div(dcc.Dropdown(
            id='attributes_keep',
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
        html.Div(id='create_component_result',
                 style={'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
    ]),
    # subcomponent table
    html.Div([
        html.H3('Subcomponents Table'),
        dcc.Store(id='cur_id'),
        dcc.Store(id='step0'),
        dcc.Store(id='step1'),
        dcc.Store(id='step2'),
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
    ])
])