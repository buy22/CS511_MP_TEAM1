from dash import Dash, dcc, html, Input, Output

from app import app, server
from apps import index1, create_subcomponents

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('| Homepage |', href='/apps/index1'),
        dcc.Link('| Create Subcomponents |', href='/apps/create_subcomponents'),
    ]),
    html.Div(id='page-content', children=[]),
    ])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/create_subcomponents':
        print(create_subcomponents.subcomponents)
        return create_subcomponents.layout
    elif pathname == '/apps/index1':
        return index1.layout
    else:
        return "No page selected!"


if __name__ == '__main__':
    app.run_server(debug=True)
