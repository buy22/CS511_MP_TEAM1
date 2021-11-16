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
from app import app
from apps import create_subcomponents

workflows = []

layout = html.Div([
    # create workflow
    html.Div([
        html.H3('Create Workflow'),
        html.Div(dcc.Input(id='workflow_name', placeholder="name of the workflow"),
                 style={'height': 30, 'margin-right': 10}),
        html.Br(),
        html.Div(dcc.Input(id='workflow_subcomponents', placeholder="subcomponent separated by ','", style={'width': '50%'}),
                 style={'display': 'flex', 'float': 'left', 'height': 30, 'width': '40%', 'margin-right': 10}),
        html.Div(dcc.Input(id='workflow_schedule', type='number', placeholder="execute how often? (mins)"),
                 style={'display': 'flex', 'float': 'right', 'height': 30, 'margin-right': 10}),
        html.Div(dcc.Input(id='workflow_dependency', type='number', placeholder="execute after which workflow?(id)"),
                 style={'display': 'flex', 'float': 'right', 'height': 30, 'margin-right': 10}),
        html.Div(html.Button('Create Workflow', id='create_workflow', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white'}),
                 style={'margin-top': 50, 'height': 50}),
        html.Div(id='create_workflow_result',
                 style={'width': '80%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
    ]),
    # subcomponent table
    html.Div([
        html.H3('Subcomponents Table'),
        dash_table.DataTable(
            id='subcomponent_table1',
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
    ]),
    # workflow table
    html.Div([
        html.H3('Workflows Table'),
        dcc.Store(id='cur_id'),
        dcc.Store(id='cur_subid'),
        dcc.Store(id='step0'),
        dcc.Store(id='step1'),
        dcc.Store(id='step2'),
        dash_table.DataTable(
            id='workflow_table',
            columns=[
                {'name': 'ID', 'id': 'workflow_table_id'},
                {'name': 'Name', 'id': 'workflow_table_name'},
                {'name': 'Schedule', 'id': 'workflow_table_schedule'},
                {'name': 'Subcomponents', 'id': 'workflow_table_subcomponents'},
                {'name': 'Status', 'id': 'workflow_table_status'},
                {'name': 'Next workflow', 'id': 'workflow_table_next'},
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
        #
        # dcc.Interval(
        # id='update_table',
        # interval=150 * 1000,
        # n_intervals=0
        # )
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
        html.Div(html.Button('Store Selected Data', id='store_selected', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white'}),
                 style={'height': 50, 'display': 'block'}),
        html.Div(html.Button('Finish Inspection', id='finish_inspection', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white'}),
                 style={'height': 50, 'display': 'block'}),
        html.Div(id='store_tmp'),
        html.Div(id='workflow_result'),

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
    ], id='visualizations')
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
    [State('workflow_name', 'value'),
     State('workflow_schedule', 'value'),
     State('workflow_subcomponents', 'value'),
     State('workflow_dependency', 'value')]
)
def create_workflow(n_clicks, workflow_name, schedule, subcomponents, dependency):
    if n_clicks:
        if schedule is not None and schedule < 0:
            return "Please input a time (in minutes) greater than 0"
        if dependency is not None:
            for w in workflows:
                if w.id == int(dependency):
                    w.dependency = len(workflows)
                    break
        if subcomponents is None:
            raise PreventUpdate
        else:
            ss = subcomponents.strip().split(',')
            s = [int(i) for i in ss]
            for i in s:
                if i < 0 or i >= len(create_subcomponents.subcomponents):
                    return "invalid subcomponent ID"
            wf = Workflow(len(workflows), workflow_name, s, schedule, "Idle")
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
    success = w.workflow_step3()
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
     Input('schedule_text', 'children'),
     Input('workflow_result', 'children')])
def update_table_list(value, children1, children2):
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
     Output('sql_query', 'style'),
     Output('visualizations', 'style')],
    [Input('dropdown1', 'value'),
     Input('dropdown2', 'value')])
def update_figure_table(value1, value2):
    if value1 == "MySQL":
        db = Mysql('team1', value2)
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'block'}, \
               {'display': 'none'}
    elif value1 == "MongoDB":
        db = MongoDB('mp_team1', value2)
        df = db.all_data()
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'none'}, \
               {'display': 'none'}
    else:
        db = Neo4j('neo4j', value2)
        df = db.all_data(value2)
        return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], {'display': 'none'}, \
               {'display': 'block'}


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
        raise PreventUpdate
    else:
        db = Mysql('team1', 'reddit_data')
        # table does not matter here, so just put in reddit_data as default
        results = db.send_query(query)
        return 'Output: {}'.format(results)


@app.callback(
    [Output('workflow_table', 'data'),
     Output('workflow_table', 'columns'),
     Output('subcomponent_table1', 'data'),
     Output('subcomponent_table1', 'columns')],
    [Input('create_workflow', 'n_clicks'),
     Input('interval-component', 'n_intervals')])
def update_workflow_table(n_clicks, n_intervals):
    to_add = []
    for workflow in workflows:
        if workflow.status == 'Workflow completed':
            workflow.status = 'Idle'
        to_add.append(workflow.to_list())
    columns = ['ID', 'Name', 'Schedule', 'Subcomponents', 'Status', 'Next workflow']
    df = pd.DataFrame(to_add, columns=columns)
    columns_subcomponent = ['ID', 'Database', 'Name', 'Score Greater Than',
                            'Controversiality Less Than', 'Author', 'Search Words']
    df1 = pd.DataFrame([i.to_list() for i in create_subcomponents.subcomponents], columns=columns_subcomponent)
    return df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], \
           df1.to_dict('records'), [{'name': i, 'id': i} for i in df1.columns]


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
            w = workflows[row]
            w.status = "Querying"
            return w.id
        else:
            raise PreventUpdate


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
    success = w.workflow_step1()
    if success:
        w.status = "Data query success"
    else:
        w.status = "Data query failed"
    time.sleep(2)
    return row


@app.callback(
    [Output('inspection_data', 'data'),
     Output('inspection_data', 'columns'),
     Output('cur_id', 'data'),
     Output('cur_subid', 'data'),
     Output('inspection_data', 'selected_rows')],
    [Input('step1', 'data'),
     Input('finish_inspection', 'n_clicks'),
     Input('store_tmp', 'children')])
def update_inspect(idx, n_clicks1, children):
    if idx is not None:
        if workflows[idx].status == 'Data query success':
            workflows[idx].status = "Inspection awaits"
        elif workflows[idx].status == 'Data query failed':
            raise PreventUpdate

        inspect_data = pd.DataFrame()
        cur_subid = -1
        for i in workflows[idx].subcomponents:
            s = create_subcomponents.subcomponents[i]
            if s.inspect_data is not None:
                inspect_data = s.inspect_data
                cur_subid = i
                break
        if workflows[idx].status == 'Storing to local database':
            return [], [], -1, -1, []
        else:
            return (inspect_data.to_dict('records'),
                    [{'name': i, 'id': i, "selectable": True} for i in inspect_data.columns],
                    idx, cur_subid, [])
    else:
        raise PreventUpdate


@app.callback(
    Output('store_tmp', 'children'),
    Input('store_selected', 'n_clicks'),
    [State('cur_subid', 'data'),
     State('cur_id', 'data'),
     State('inspection_data', 'selected_rows'),
     State('inspection_data', 'data')])
def store_selected(n_clicks, subid, idx, selected_rows, data):
    if n_clicks == 0:
        raise PreventUpdate
    if subid is not None and subid >= 0:
        if idx is not None and idx >= 0:
            create_subcomponents.subcomponents[subid].inspect_data = None
            res = []
            if data:
                for i in selected_rows:
                    res.append(data[i])
            create_subcomponents.subcomponents[subid].strict_data = \
                create_subcomponents.subcomponents[subid].strict_data.append(res)
            return 'Data of subcomponent with id {} in workflow {} has been pushed'.format(str(subid), str(idx))


@app.callback(
    [Output('workflow_result', 'children'),
     Output('workflow_table', 'active_cell'),
     Output('start_workflow', 'n_clicks')],
    Input('finish_inspection', 'n_clicks'),
    [State('cur_id', 'data')])
def finish_inspection(n_clicks, cur_id):
    if n_clicks == 0:
        raise PreventUpdate
    if cur_id is not None and cur_id >= 0:
        idx = cur_id
        if workflows[idx].status != 'Inspection awaits':
            return 'No inspection in progress', {'row': 0, 'column': 0, 'column_id': 'ID'}, 0
        workflows[idx].status = 'Storing to local database'
        success = workflows[idx].workflow_step2()
        if success:
            workflows[idx].status = 'Workflow completed'
            success_step3 = workflows[idx].workflow_step3()
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
    raise PreventUpdate


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
    [Output('word-cloud-figure', 'figure'), Output('word-count-figure', 'figure'),
     Output('word-relation-figure', 'figure')],
    [Input('dropdown1', 'value'), Input('text_visualize_key_word', 'value')]
)
def update_figure(selected_database,
                  keyword):  # don't know the year tag in sample dataset means, if we know, we can plot dataset by year. selected_year=2015
    if selected_database == "MySQL":
        raise PreventUpdate
    elif selected_database == "MongoDB":
        raise PreventUpdate
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

        # generate word relation
        npt.build_graph(stopwords=stopwords, min_edge_frequency=1)
        fig_relation = npt.co_network(title='Co-occurrence network')
        return fig_wordcloud, fig_wordcount, fig_relation
