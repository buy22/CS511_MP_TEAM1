import json
import time

from Visualization import NLPlot
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
from wordcloud import WordCloud

from Mysql import Mysql
from Neo4j import Neo4j
from mongoDB import MongoDB
from workflow import Workflow

# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
workflows = []

app.layout = html.Div([
    dcc.Store(id='database'),
    # select database
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
            value='Neo4j'
        )
    ]),
    # create workflow
    html.Div([
        html.H3('Create Workflow'),
        html.Div(dcc.Dropdown(
            id='attributes_keep',
            options=[],
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
        html.Div(html.Button('Create Workflow', id='create_workflow', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white'}),
                 style={'margin-top': 50, 'height': 50}),
        html.Div(id='create_workflow_result',
                 style={'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
    ]),
    # workflow table
    html.Div([
        html.H3('Workflows Table'),
        dcc.Store(id='cur_id'),
        dcc.Store(id='step0'),
        dcc.Store(id='step1'),
        dcc.Store(id='step2'),
        dash_table.DataTable(
            id='workflow_table',
            columns=[
                {'name': 'ID', 'id': 'workflow_table_id'},
                {'name': 'Database', 'id': 'workflow_table_db'},
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
        ),
        # for live updating figures
        dcc.Interval(
            id='interval-component',
            interval=1500,  # in milliseconds
            n_intervals=0
        ),
        dcc.Interval(
            id='scheduling',
            interval=60 * 1000,
            n_intervals=0
        ),
        dcc.Interval(
            id='update_table',
            interval=150 * 1000,
            n_intervals=0
        )
    ]),
    html.Div(id='workflow_click_data', style={'whiteSpace': 'pre-wrap'}),
    html.Div(html.Button('Initiate Workflow', id='start_workflow', n_clicks=0,
                         style={'background-color': 'black', 'color': 'white'}),
             style={'height': 50, 'display': 'block'}),
    html.Div(id='workflow_started', style={'display': 'none'}),
    html.Div(id='schedule_text', style={'display': 'none'}),
    # Manage, View and Query Data
    html.Div([
        html.H3('Manage, View and Query Data'),
        # data requiring inspection in incoming workflows
        html.H4('Data Inspections Table'),
        dash_table.DataTable(
            id='inspection_data',
            style_cell={'textAlign': 'left', 'overflow': 'hidden', 'maxWidth': 0, 'textOverflow': 'ellipsis'},
            style_table={'overflowY': 'show'},
            row_selectable="multi",
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
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
        html.Div(id='inspection_click_data', style={'whiteSpace': 'pre-wrap'}),
        html.Div(html.Button('Store selected data', id='finish_inspection', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white'}),
                 style={'height': 50, 'display': 'block'}),
        html.Div(id='workflow_result'),

        # Mysql query section
        html.Div([
            html.H4('Query for MySQL'),
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

        # views of various tables/collections
        html.Div([
            html.H6('Select your table/collection/label'),
            dcc.Dropdown(
                id='dropdown2',
                options=[], style={'width': '50%'}
            )
        ], style={'height': 100}),
        html.H4('Database View'),
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
    ]),
    # Text data visualization
    html.Div([
        html.H3('Text data visualization'),
        dcc.Input(
            id='text_visualize_key_word',
            placeholder='Input your keywords here, default: Disease',
            value='Disease'
        ),
        # might try slider with time rather than input next week
        html.Div([dcc.Graph(id='word-cloud-figure')]),
        html.Div([dcc.Graph(id='word-count-figure')]),
        html.Div([dcc.Graph(id='word-relation-figure')]),
    ])
])


@app.callback(
    Output('attributes_keep', 'options'),
    Input('dropdown1', 'value'))
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
        if condition2 is not None and (int(condition2) < 0 or int(condition2) > 1):
            return "Invalid controversiality"
        if dependency is not None:
            for w in workflows:
                if w.id == int(dependency):
                    w.dependency = len(workflows)
                    break
        wf = Workflow(db, len(workflows), workflow_name, schedule, "Idle",
                      [condition1, condition2, condition3, condition4], attributes)
        workflows.append(wf)
        return ""


@app.callback(
    Output('schedule_text', 'children'),
    Input('scheduling', 'n_intervals'))
def schedule_workflows(n_intervals):
    can_start = True
    execution_list = []
    for idx, i in enumerate(workflows):
        if not i.wait_time:
            continue
        if i.status != "Idle":
            can_start = False
        i.wait_time = max(i.wait_time - 1, 0)
        if i.wait_time == 0:
            execution_list.append(idx)

    if not can_start:
        raise PreventUpdate
    for i in execution_list:
        automation(i)
    return 'Scheduled workflow executed'


def automation(i):
    w = workflows[i]
    w.status = "Querying"
    success = w.workflow_step1(scheduled=True)
    if not success:
        raise PreventUpdate
    w.status = "Data query success"
    success = w.workflow_step2(scheduled=True)
    if not success:
        raise PreventUpdate
    w.status = "Storing to local database"
    _, success = w.workflow_step3()
    if not success:
        raise PreventUpdate
    w.status = "Workflow completed"
    w.wait_time = w.schedule
    if w.dependency:
        automation(w.dependency)


@app.callback(
    [Output('dropdown2', 'options'),
     Output('dropdown2', 'value')],
    [Input('dropdown1', 'value'),
     Input('update_table', 'n_intervals'),
     Input('workflow_result', 'children')])
def update_table_list(value, n_intervals, children):
    if value == "MySQL":
        db = Mysql('team1', 'reddit_data')  # again, table name unimportant for "show tables" query
        opts = db.find_all_collections()
        # show tables query returns list of tuples for some reason
        options = [{'label': opt[0], 'value': opt[0]} for opt in opts]
        return options, options[0]['value']
    elif value == "MongoDB":
        db = MongoDB('mp_team1')
        opts = db.find_all_collections()
        options = [{'label': opt, 'value': opt} for opt in opts]
        return options, options[0]['value']
    else:  # Neo4j - no tables, return nanme of lables instead
        db = Neo4j('neo4j')
        opts = db.find_all_collections()
        options = [{'label': opt, 'value': opt} for opt in opts]
        return options, options[0]['value']


@app.callback(
    [Output('live_update_table', 'data'),
     Output('live_update_table', 'columns'),
     Output('sql_query', 'style')],
    [Input('dropdown1', 'value'),
     Input('dropdown2', 'value'),
     Input('workflow_result', 'children')])
def update_figure_table(value1, value2, children):
    if value1 == "MySQL":
        db = Mysql('team1', value2)
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'block'}
    elif value1 == "MongoDB":
        db = MongoDB('mp_team1', value2)
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'none'}
    else:
        db = Neo4j('neo4j', value2)
        df = db.all_data(value2)
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'none'}


@app.callback(
    Output('click_data', 'children'),
    [Input('live_update_table', 'active_cell')],
    [State('live_update_table', 'data')])
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
    Output('inspection_click_data', 'children'),
    Input('inspection_data', 'active_cell'),
    State('inspection_data', 'data'))
def display_insepect_click_data(active_cell, table_data):
    if active_cell:
        cell = json.dumps(active_cell, indent=2)
        row = active_cell['row']
        col = active_cell['column_id']
        value = table_data[row][col]
        out = '%s' % value
    else:
        out = 'no cell selected/no data in the table'
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
     Input('interval-component', 'n_intervals')])
def update_workflow_table(n_clicks, n_intervals):
    to_add = []
    for workflow in workflows:
        if workflow.status == 'Workflow completed':
            workflow.status = 'Idle'
        to_add.append(workflow.to_list())
    columns = ['ID', 'Database', 'Name', 'Schedule', 'Status', 'Score Greater Than',
               'Controversiality Less Than', 'Author', 'Search Words', 'Next workflow']
    df = pd.DataFrame(to_add, columns=columns)
    return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns]


@app.callback(
    Output('step0', 'data'),
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
            return w.id
        else:
            return None


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
    time.sleep(2)
    return pd.DataFrame.from_records([{'strict': strict_data, 'inspect': inspect_data, 'id': row}]).to_json(
        date_format='iso', orient='split')


@app.callback(
    [Output('inspection_data', 'data'),
     Output('inspection_data', 'columns'),
     Output('cur_id', 'data'),
     Output('inspection_data', 'selected_rows')],
    [Input('step1', 'data'),
     Input('finish_inspection', 'n_clicks')])
def update_inspect(json_data, n_clicks):
    if json_data:
        data = pd.read_json(json_data, orient='split')
        _, inspect_data, idx = data['strict'], data['inspect'], data['id']
        idx = idx[0]
        inspect_data = workflows[idx].inspect_data
        if type(inspect_data) == list:
            inspect_data = pd.DataFrame()
        if workflows[idx].status == 'Storing to local database':
            return ([], [],
                    pd.DataFrame.from_records([{'id': -1}]).to_json(date_format='iso', orient='split'), [])
        else:
            return (inspect_data.to_dict('records'),
                    [{'name': i, 'id': i, "selectable": True} for i in inspect_data.columns],
                    pd.DataFrame.from_records([{'id': idx}]).to_json(date_format='iso', orient='split'), [])
    else:
        raise PreventUpdate


@app.callback(
    [Output('workflow_result', 'children'),
     Output('workflow_table', 'active_cell'),
     Output('start_workflow', 'n_clicks')],
    Input('finish_inspection', 'n_clicks'),
    [State('inspection_data', 'selected_rows'),
     State('inspection_data', 'data'),
     State('cur_id', 'data')])
def finish_inspection(n_clicks, selected_rows, data, cur_id):
    if n_clicks == 0:
        raise PreventUpdate
    res = []
    if data:
        for i in selected_rows:
            res.append(data[i])
    if cur_id:
        idx = pd.read_json(cur_id, orient='split')['id'][0]
        if workflows[idx].status != 'Data query success':
            return 'No inspection in progress', {'row': 0, 'column': 0, 'column_id': 'ID'}, 0
        print(workflows[idx].status)
        workflows[idx].retrieve_inspect_data(res)
        workflows[idx].status = 'Storing to local database'
        success = workflows[idx].workflow_step2()
        if success:
            workflows[idx].status = 'Workflow completed'
            _, success_step3 = workflows[idx].workflow_step3()
            row, button = 0, 0
            if workflows[idx].dependency:
                row = workflows[idx].dependency
                button = 1
            if success_step3:
                return 'Workflow {} completed'.format(str(idx)), {'row': row, 'column': 0, 'column_id': 'ID'}, button
            else:
                return 'Workflow {} returned empty result. No write to database'.format(str(idx)), {'row': row,
                                                                                                    'column': 0,
                                                                                                    'column_id': 'ID'}, button
        else:
            raise Exception


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


# Text data visualization
@app.callback(
    [Output('word-cloud-figure', 'figure'), Output('word-count-figure', 'figure'), Output('word-relation-figure', 'figure')],
    [Input('dropdown1', 'value'), Input('text_visualize_key_word', 'value')]
)
def update_figure(selected_database,
                  keyword):  # don't know the year tag in sample dataset means, if we know, we can plot dataset by year. selected_year=2015
    if selected_database == "MySQL":
        db = Mysql('team1', 'reddit_data')
    elif selected_database == "MongoDB":
        db = MongoDB('mp_team1', 'comments')
    else:
        db = Neo4j('neo4j')
    body_df = db.get_keyword_reddit(keyword)

    # generate word cloud
    wordcloud = WordCloud(width=1200, height=600, max_font_size=150, background_color='white').generate(
        ' '.join(body_df))
    fig_wordcloud = px.imshow(wordcloud.to_array())

    # generate word count
    stopwords = list(map(str.strip, open('stopwords').readlines()))
    npt = NLPlot(pd.DataFrame(body_df), target_col='Reddit.body')
    fig_wordcount = npt.bar_ngram(title='uni-gram', ngram=1, top_n=50, stopwords=stopwords)

    #generate word relation
    npt.build_graph(stopwords=stopwords, min_edge_frequency=1)
    fig_relation=npt.co_network(title='Co-occurrence network')
    return fig_wordcloud, fig_wordcount, fig_relation


if __name__ == '__main__':
    app.run_server(debug=True)
