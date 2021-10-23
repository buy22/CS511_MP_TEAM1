from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
from Mysql import Mysql
from mongoDB import MongoDB
from workflow import Workflow
import pandas as pd
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# this css is not good
app = Dash(__name__, external_stylesheets=external_stylesheets)

workflows = []

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
        html.H3('Section 1: Create Workflow'),
        html.Div(dcc.Input(id='workflow_name', placeholder="name of the workflow"),
                 style={'height': 30, 'margin-right': 10}),
        html.Br(),
        html.Div(dcc.Input(id='condition1', type='number', placeholder="score greater than?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(dcc.Input(id='condition2', type='number', placeholder="controversiality less than?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(dcc.Input(id='condition3', placeholder="which author?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        # currently MySQL will assume that only one word is inputted (ex. if multiple words are given),
        # they will not be treated separately in the query. something that I can probably fix after the MP
        html.Div(dcc.Input(id='condition4', placeholder="what keyword to search?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(html.Button('Create Workflow', id='create_workflow', n_clicks=0),
                 style={'height': 50}),
        html.Div(id='create_workflow_result',
                 style={'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
    ]),
    html.Div([
        html.H3('Section 2: Workflows'),
        dash_table.DataTable(
            id='workflow_table',
            columns=[
                {'name': 'ID', 'id': 'workflow_table_id'},
                {'name': 'Name', 'id': 'workflow_table_name'},
                {'name': 'Schedule', 'id': 'workflow_table_schedule'},
                {'name': 'Score Greater Than', 'id': 'workflow_table_score'},
                {'name': 'Controversiality Less Than', 'id': 'workflow_table_controversiality'},
                {'name': 'Author', 'id': 'workflow_table_author'},
                {'name': 'Search Words', 'id': 'workflow_table_search'},
            ],
            data=[],
            style_cell={'textAlign': 'left', 'overflow': 'hidden', 'maxWidth': 0, 'textOverflow': 'ellipsis'},
            style_table={'overflowY': 'show'},
            page_current=0,
            page_size=10,
        )
    ]),
    html.Div([
        html.H3('Section 3: Query and View Data'),
        html.Div([
            html.Div(dcc.Textarea(
                    id='custom_query',
                    placeholder='Enter your MySQL query here...',
                    style={'width': '80%', 'height': 150},
                ),
                 style=dict(display='block', justifyContent='center')),
            html.Div(html.Button('Query', id='submit_query', n_clicks=0),
                     style=dict(display='block', justifyContent='center')),
            html.Div(
                html.H4('Query Results')
                , style= {'display': 'block'}
            ),
            html.Div(id='query_result',
                     style={'display': 'block', 'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
            html.Br()], id='sql_query', style={'display': 'block'}),

        html.Div([
            html.H6('Select your table/collection'),
            dcc.Dropdown(
                id='dropdown2',
                options=[],
            )
        ], style={'height': 100}),
        dash_table.DataTable(
            id='live_update_table',
            style_cell={'textAlign': 'left', 'overflow': 'hidden', 'maxWidth': 0, 'textOverflow': 'ellipsis'},
            style_table={'overflowY': 'show'},
            data=[],
            page_current=0,
            page_size=10,
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
    # for live updating figures
    dcc.Interval(
        id='interval-component',
        interval=3*1000,  # in milliseconds
        n_intervals=0
    )
'''


@app.callback(
    Output('create_workflow_result', 'children'),
    Input('create_workflow', 'n_clicks'),
    [State('condition1', 'value'),
     State('condition2', 'value'),
     State('condition3', 'value'),
     State('condition4', 'value'),
     State('workflow_name', 'value')]
)
def create_workflow(n_clicks, condition1, condition2, condition3, condition4, workflow_name):
    if n_clicks:
        wf = Workflow(len(workflows), workflow_name, None, [condition1, condition2, condition3, condition4])
        workflows.append(wf)
        return ""


@app.callback(
    [Output('dropdown2', 'options'),
     Output('dropdown2', 'value')],
    Input('dropdown1', 'value'))
def update_figure_table(value): # , n_intervals
    if value == "MySQL":
        db = Mysql('team1')
        opts = db.find_all_collections()
        # show tables query returns list of tuples for some reason
        options = [{'label': opt[0], 'value': opt[0]} for opt in opts]
        return options, options[0]['value']
    elif value == "MongoDB":
        db = MongoDB('mp_team1')
        opts = db.find_all_collections()
        options = [{'label': opt, 'value': opt} for opt in opts]
        return options, options[0]['value']
    else: # Neo4j
        return [], None


@app.callback(
    [Output('live_update_table', 'data'),
     Output('live_update_table', 'columns'),
     Output('sql_query', 'style'),],
    [Input('dropdown1', 'value'),
     Input('dropdown2', 'value')]
    #Input('interval-component', 'n_intervals')
    )
def update_figure_table(value1, value2): # , n_intervals
    if value1 == "MySQL":
        db = Mysql('team1', value2)
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'block'}
    elif value1 == "MongoDB":
        db = MongoDB('mp_team1', value2)
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'none'}
    else: # Neo4j
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
    State('custom_query', 'value')
)
def execute_query(n_clicks, query):
    if n_clicks == 0:
        # execute_query fires immediately
        # and displays an error since there is no query to return...
        # this will prevent that from occurring until a query is sent.
        raise PreventUpdate
    else:
        db = Mysql('team1')
        results = db.send_query(query)
        return 'Output: {}'.format(results)


@app.callback(
    [Output('workflow_table', 'data'),
     Output('workflow_table', 'columns')],
    [Input('create_workflow', 'n_clicks')]
    )
def update_workflow_table(n_clicks): # should update each time a new workflow is made
    to_add = []
    for workflow in workflows:
        to_add.append(workflow.to_list())
    columns = ['ID', 'Name', 'Schedule', 'Score Greater Than', 'Controversiality Less Than', 'Author', 'Search Words']
    df = pd.DataFrame(to_add, columns=columns)
    return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]


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
