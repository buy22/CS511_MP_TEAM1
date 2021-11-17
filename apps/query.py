from Mysql import Mysql
from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
from app import app, server

# Mysql query section
layout = html.Div([
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
            html.Br()], id='sql_query', style={'display': 'block'})


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