from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
from Mysql import Mysql
from mongoDB import MongoDB
from Neo4j import Neo4j
from workflow import Workflow
import pandas as pd
import json
import time

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# this css is not good
app = Dash(__name__, external_stylesheets=external_stylesheets)

workflows = []
inspection_data = []


def get_columns():
    db = Mysql('team1', 'reddit_data')
    # db=Neo4j('neo4j')
    df = db.all_data()
    cols = df.columns
    return [{'label': opt, 'value': opt} for opt in cols]


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
            style={'width': '50%'},
            value='MySQL'
        )
    ]),
    html.Div([
        html.H3('Section 1: Create Workflow'),
        html.Div(dcc.Dropdown(
            id='attributes_keep',
            options=get_columns(),
            value=[], placeholder='select attributes to keep',
            multi=True
        ), style={'height': 50}),
        html.Div(dcc.Input(id='workflow_name', placeholder="name of the workflow"),
                 style={'height': 30, 'margin-right': 10}),
        html.Br(),
        html.Div(dcc.Input(id='condition1', type='number', placeholder="score greater than?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(dcc.Input(id='condition2', type='number', placeholder="controversiality (0 or 1)"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        html.Div(dcc.Input(id='condition3', placeholder="which author?"),
                 style={'display': 'flex', 'float': 'left', 'height': 50, 'margin-right': 10}),
        # currently MySQL will assume that only one word is inputted (ex. if multiple words are given),
        # they will not be treated separately in the query. something that I can probably fix after the MP
        html.Div(dcc.Input(id='condition4', placeholder="what keyword to search?"),
                 style={'display': 'flex', 'float': 'left', 'height': 30, 'margin-right': 10}),
        html.Div(dcc.Input(id='workflow_schedule', type='number', placeholder="execute how often? (mins)"),
                 style={'display': 'flex', 'float': 'left', 'height': 30, 'margin-right': 10}),
        html.Div(dcc.Input(id='workflow_dependency', type='number', placeholder="execute after which workflow?(id)"),
                 style={'display': 'flex', 'float': 'right', 'height': 30, 'margin-right': 10}),
        html.Div(html.Button('Create Workflow', id='create_workflow', n_clicks=0),
                 style={'margin-top': 50, 'height': 50}),
        html.Div(id='create_workflow_result',
                 style={'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
    ]),
    html.Div([
        html.H3('Section 2: Workflows'),
        dcc.Store(id='step0'),
        dcc.Store(id='step1'),
        dcc.Store(id='step2'),
        dash_table.DataTable(
            id='workflow_table',
            columns=[
                {'name': 'ID', 'id': 'workflow_table_id'},
                {'name': 'Name', 'id': 'workflow_table_name'},
                {'name': 'Schedule', 'id': 'workflow_table_schedule'},
                {'name': 'Status', 'id': 'workflow_table_status'},
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
    html.Div(id='workflow_click_data', style={'whiteSpace': 'pre-wrap'}),
    html.Div(html.Button('Initiate Workflow', id='start_workflow', n_clicks=0),
                 style={'height': 50, 'display': 'block'}),
    html.Div(id='workflow_started', style={'display': 'none'}),
    html.Div(id='workflow_inspect', style={'display': 'none'}),
    html.Div([
        html.H3('Section 3: Query and View Data'),
        # Mysql query section
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
                , style={'display': 'block'}
            ),
            html.Div(id='query_result',
                     style={'display': 'block', 'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
            html.Br()], id='sql_query', style={'display': 'block'}),

        # data requiring inspection in incoming workflows
        dash_table.DataTable(
            id='inspection_data',
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

        # views of various tables/collections
        html.Div([
            html.H6('Select your table/collection'),
            dcc.Dropdown(
                id='dropdown2',
                options=[], style={'width': '50%'}
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
     State('workflow_name', 'value'),
     State('attributes_keep', 'value'),
     State('workflow_schedule', 'value'),
     State('workflow_dependency', 'value'),
     State('dropdown1', 'value')]
)
def create_workflow(n_clicks, condition1, condition2, condition3, condition4,
                    workflow_name, attributes, schedule, dependency, db):
    if n_clicks:
        if schedule is not None and schedule < 0:
            return "Please input a time (in minutes) greater than 0"
        if condition2 is not None and (int(condition2) < 0  or int(condition2) > 1):
            return "Invalid controversiality"
        wf = Workflow(db, len(workflows), workflow_name, schedule, "Not Started",
                      [condition1, condition2, condition3, condition4], attributes, dependency)
        workflows.append(wf)
        return ""


@app.callback(
    [Output('dropdown2', 'options'),
     Output('dropdown2', 'value')],
    Input('dropdown1', 'value'))
def update_figure_table(value): # , n_intervals
    if value == "MySQL":
        db = Mysql('team1', 'reddit_data') # again, table name unimportant for "show tables" query
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
        db=Neo4j()
        opts = db.find_all_collections()
        options = [{'label': opt, 'value': opt} for opt in opts]
        return options, options[0]['value']
        options, options[0]['value']


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
    else: #
        db = MongoDB('neo4j')
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'none'}


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
        db = Mysql('team1', 'reddit_data') 
        # table does not matter here, so just put in reddit_data as default
        results = db.send_query(query)
        return 'Output: {}'.format(results)


@app.callback(
    [Output('workflow_table', 'data'),
     Output('workflow_table', 'columns')],
    [Input('create_workflow', 'n_clicks'),
     Input('workflow_started', 'children'),
     Input('workflow_inspect', 'children'),
     Input('step1', 'data')])
def update_workflow_table(n_clicks, children1, children2, step1): # should update each time a new workflow is made
    to_add = []
    for workflow in workflows:
        to_add.append(workflow.to_list())
    columns = ['ID', 'Name', 'Schedule', 'Status', 'Score Greater Than', 'Controversiality Less Than', 'Author', 'Search Words']
    df = pd.DataFrame(to_add, columns=columns)
    return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]


@app.callback(
    [Output('workflow_started', 'children'),
     Output('step0', 'data')],
    Input('start_workflow', 'n_clicks'),
    [State('workflow_table', 'active_cell')])
def initiate_selected_workflow(n_clicks, active_cell):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        if active_cell:
            row = active_cell['row']
            w = None
            for wf in workflows:
                if wf.id == row:
                    w = wf
                    break
            w.status = "Querying"
            return None, w.id
        else:
            return None, None


@app.callback(
    Output('step1', 'data'),
    Input('step0', 'data'))
def step1(row):
    w = None
    for wf in workflows:
        if wf.id == row:
            w = wf
            break
    if not w:
        return
    strict_data, inspect_data, success = w.workflow_step1()
    if success:
        w.status = "Data query success"
    else:
        w.status = "Data query failed"
    return pd.DataFrame.from_records([{'strict': strict_data, 'inspect': inspect_data, 'id': row}]).to_json(
                date_format='iso', orient='split')


@app.callback(
    [Output('inspection_data', 'data'),
     Output('inspection_data', 'columns'),
     Output('workflow_inspect', 'children')],
    Input('step1', 'data'))
def update_inspect(json_data): # , n_intervals
    if json_data:
        data = pd.read_json(json_data, orient='split')
        _, inspect_data, idx = data['strict'], data['inspect'], data['id']
        db = Mysql('team1', 'reddit_data')
        cols = db.all_data().columns
        inspect_data = pd.DataFrame(data=inspect_data[0], columns=cols)
        idx = idx[0]
        time.sleep(3)
        for wf in workflows:
            if wf.id == idx:
                break
            wf.status = "Human inspection(if qualify)"
        return (inspect_data.to_dict('records'),
                [{'name': i, 'id': i}for i in inspect_data.columns],
                None)
    else:
        return pd.DataFrame().to_dict('records'), [], None


@app.callback(
    Output('workflow_click_data', 'children'),
    [Input('workflow_table', 'active_cell')],
    [State('workflow_table', 'data')])
def display_workflow_click_data(active_cell, table_data):
    if active_cell:
        cell = json.dumps(active_cell, indent=2)
        row = active_cell['row']
        value = table_data[row]
        out = 'Selected workflow: ' + '%s' % value
        return out
    else:
        return 'no workflow selected'


if __name__ == '__main__':
    app.run_server(debug=True)
