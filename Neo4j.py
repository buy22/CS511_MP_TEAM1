import time

import pandas as pd
from neo4j import GraphDatabase



# from py2neo import Graph, Node, Relationship

class Neo4j:
    def __init__(self, db, label='Reddit,Author,SubReddit'):
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "123456"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = self.driver.session(database=db)
        self.label = label

    def close(self):
        self.session.close()

    def node_output_to_dataframe(self, neo4j_graph_data):
        df_list = pd.concat([pd.DataFrame.from_dict({(i, j): data[i][j]
                                                     for i in data.keys()
                                                     for j in data[i].keys()},
                                                    orient='index').transpose() for data in neo4j_graph_data])
        df_list.columns = ['_'.join(col) for col in df_list.columns.values]
        return df_list

    def all_data(self, label='Reddit,Author,SubReddit'):
        # query = "MATCH (m:Author)-[:Author]->(n:Reddit) RETURN Reddit.body,n.score,n.controversiality,m.name LIMIT 25"
        # print(label)
        if 'workflow' not in label:
            query = "MATCH (Author:Author)-[:Author]->(Reddit:Reddit)<-[:subreddit]-(SubReddit:SubReddit) RETURN " + self.label + " LIMIT 25"
            data = self.node_output_to_dataframe(self.session.run(query).data())
        else:
            data = pd.read_csv('Neo4j_workflow_output/' + label)

        # print(data)
        return data

    def workflow_step1(self, cond):
        strict_conditions = ""
        inspection_conditions = ""

        already_started_condition = False
        # score >
        if str(cond[0]) and cond[0] is not None:
            already_started_condition = True
            strict_conditions = "WHERE Reddit.score > " + str(cond[0])
            inspection_conditions = "WHERE Reddit.score > " + str(max(cond[0] - 10, 0))
        # controversiality =
        if str(cond[1]) and cond[1] is not None:
            if already_started_condition:
                strict_conditions += " AND Reddit.controversiality = " + str(cond[1])
                inspection_conditions += ""
            else:
                already_started_condition = True
                strict_conditions = "WHERE Reddit.controversiality = " + str(cond[1])
                inspection_conditions = "WHERE "
        # author =
        if cond[2] and cond[2] is not None and cond[2] != "":
            if already_started_condition:
                strict_conditions += " AND Author.name = '" + cond[2] + "'"
                inspection_conditions += " AND Author.name = '" + cond[2] + "'"
            else:
                already_started_condition = True
                strict_conditions = "WHERE Author.name = '" + cond[2] + "'"
                inspection_conditions = "WHERE Author.name = '" + cond[2] + "'"
        # partial text search in body
        if cond[3] and cond[3] is not None and cond[3] != "":
            if already_started_condition:
                strict_conditions += " AND Reddit.body CONTAINS '" + cond[3] + "'"
                inspection_conditions += " AND Reddit.body CONTAINS '" + cond[3] + "'"
            else:
                already_started_condition = True
                strict_conditions = "WHERE Reddit.body CONTAINS '" + cond[3] + "'"
                inspection_conditions = "WHERE Reddit.body CONTAINS '" + cond[3] + "'"

        try:
            strict_query = "MATCH (Author:Author)-[:Author]->(Reddit:Reddit)<-[:subreddit]-(SubReddit:SubReddit) " + strict_conditions + " RETURN Reddit,Author,SubReddit LIMIT 20"
            inspection_query = "MATCH (Author:Author)-[:Author]->(Reddit:Reddit)<-[:subreddit]-(SubReddit:SubReddit) " + inspection_conditions + " RETURN Reddit,Author,SubReddit LIMIT 20"

            strict_data = self.node_output_to_dataframe(self.session.run(strict_query).data())
            inspection_data = self.node_output_to_dataframe(self.session.run(inspection_query).data())

            # remove  duplicate in inspection_data
            # cond = inspection_data['Reddit_redditID'].isin(strict_data['Reddit_redditID'])
            # inspection_data=inspection_data.drop(inspection_data[cond].index, inplace=True)
            inspection_data = inspection_data.append(strict_data).drop_duplicates(keep=False)

            # print(inspection_data)
            time.sleep(3)
            return strict_data, inspection_data, True
        except Exception as ex:
            return None, None, False

    def workflow_step2(self, strict_data, inspection_data):
        try:
            res = strict_data.append(inspection_data)
            # time.sleep(3)
            return res, True
        except Exception as ex:
            return None, False

    def dataframe_to_neo(self, df, nodename):
        for index, row in df.iterrows():
            query = '''MERGE(n:Node {attr0: $attr0_value})'''
            # print(nodename, df.columns[0], row[0])
            self.session.run(query, parameters={'Node': nodename, 'attr0': df.columns[0], 'attr0_value': row[0]})
        return 'success! ' + nodename

    def workflow_step3(self, data, attributes, node):
        # df = data[data.columns.intersection(attributes)]
        # print(attributes)
        # print(data)
        # print(node)
        # self.dataframe_to_neo(df, node)
        # # time.sleep(3)
        # return df, True
        try:
            df = data[data.columns.intersection(attributes)]
            df.to_csv('Neo4j_workflow_output/' + node + '.csv')
            # self.dataframe_to_neo(df,node)
            # time.sleep(3)
            return df, True
        except Exception as ex:
            return None, False

    def find_all_collections(self):  # return labels in Neo4j and Neo4j_workflow_output/ filefolder
        query = "call db.labels()"
        rows = [dict.get('label') for dict in self.session.run(query).data()]

        from os import listdir
        from os.path import isfile, join
        mypath = 'Neo4j_workflow_output/'
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        return rows + files

    # don't know the year tag in sample dataset means, if we know, we can plot dataset by year
    def get_keyword_reddit(self, keyword):
        # get reddit body data that contains keyword
        query = "MATCH (Reddit:Reddit) " \
                "where toLower(Reddit.body) CONTAINS toLower('" + keyword + "') " \
                                                                            "RETURN Reddit.body"
        data = pd.DataFrame(self.session.run(query).data())
        # convert sting to lower case
        body_df = data['Reddit.body'].str.lower()
        return body_df


# db=Neo4j('neo4j')
# body_df=db.get_keyword_reddit('disease')
#
# from wordcloud import WordCloud
# import plotly.express as px
# import nlplot
# import plotly.io as pio
# pio.renderers.default = "browser"
# # target_col as a list type or a string separated by a space.
# npt = nlplot.NLPlot(pd.DataFrame(body_df), target_col='Reddit.body')
#
# # Stopword calculations can be performed.
# stopwords = list(map(str.strip, open('stopwords').readlines()))
#
# fig=npt.bar_ngram(title='uni-gram', ngram=1, top_n=50, stopwords=stopwords)
# fig.show()
#
# npt.build_graph(stopwords=stopwords, min_edge_frequency=1)
# fig=npt.co_network(title='Co-occurrence network')
# fig.show()
#
# wordcloud = WordCloud(width=1200, height=600, max_font_size=150, background_color='white').generate(
#         ' '.join(body_df))
# # save to file foder
# wordcloud.to_file('Word_Clouds/word_cloud.png')
# fig=px.imshow(wordcloud.to_array())
# fig.show()

