import json

from Visualization import NLPlot
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
from wordcloud import WordCloud

from Neo4j import Neo4j
from workflow import Workflow
from app import app

# Text data visualization
layout = html.Div([
    html.Div([
        html.H3('Text data visualization'),
        dcc.Input(
            id='text_visualize_key_word',
            placeholder='Input your keywords here, default: Disease',
            value='Disease'
        ),
        html.Button('Visualize', id='submit_visualize', n_clicks=0),
        # might try slider with time rather than input next week
        html.Div([dcc.Graph(id='word-cloud-figure')]),
        html.Div([dcc.Graph(id='word-count-figure')]),
        html.Div([dcc.Graph(id='word-relation-figure')]),
    ], id='visualizations')
])

# Text data visualization
@app.callback(
    [Output('word-cloud-figure', 'figure'),
     Output('word-count-figure', 'figure'),
     Output('word-relation-figure', 'figure'),
     ],
    [Input('text_visualize_key_word', 'value'),
     Input('submit_visualize', 'n_clicks')]
)
def update_figure(keyword,n_clicks):
    if n_clicks == 0:
        raise PreventUpdate
    # don't know the year tag in sample dataset means, if we know, we can plot dataset by year. selected_year=2015
    else:
        db = Neo4j('neo4j')
        body_df = db.get_keyword_reddit(keyword)

        # generate word cloud
        wordcloud = WordCloud(width=1200, height=600, max_font_size=150, background_color='white').generate(
            ' '.join(body_df))
        fig_wordcloud = px.imshow(wordcloud.to_array(),width=1200,height=600)

        # generate word count
        stopwords = list(map(str.strip, open('stopwords').readlines()))
        npt = NLPlot(pd.DataFrame(body_df), target_col='Reddit.body')
        fig_wordcount = npt.bar_ngram(title='uni-gram', ngram=1, top_n=50, stopwords=stopwords)

        # generate word relation
        npt.build_graph(stopwords=stopwords, min_edge_frequency=1)
        fig_relation = npt.co_network(title='Co-occurrence network')
        return fig_wordcloud, fig_wordcount, fig_relation