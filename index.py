from dash import Dash, dcc, html, Input, Output

from app import app, server
from apps import index1, create_subcomponents, query, text_visualization

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('| Homepage |', href='/apps/index1', style={'font-size':'15px'}),
        dcc.Link('| Create Subcomponents |', href='/apps/create_subcomponents', style={'font-size':'15px'}),
        dcc.Link('| Query MySQL Data |', href='/apps/query', style={'font-size':'15px'}),
        dcc.Link('| Text Data Visualization |', href='/apps/text_visualization', style={'font-size':'15px'}),
    ]),
    html.Div(id='page-content', children=[], style={'font-size':'15px'}),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/create_subcomponents':
        return create_subcomponents.layout
    elif pathname == '/apps/index1':
        return index1.layout
    elif pathname == '/apps/query':
        return query.layout
    elif pathname == '/apps/text_visualization':
        return text_visualization.layout
    else:
        return "No page selected!"


if __name__ == '__main__':
    app.run_server(debug=True)
