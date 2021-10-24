import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import time


class Mysql:
    def __init__(self, db, table):
        self.cnx = None
        self.cursor = None
        self.database = db
        self.table = table

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(user='cs511', password='databaesCS511',
                                               host='127.0.0.1', database=self.database)
        except Exception as ex:
            raise ex

    def query(self, value):
        self.cursor = self.cnx.cursor()
        query = ("SELECT * FROM reddit_data"
                 "HAVING author = {}".format(value))
        self.cursor.execute(query)
        res = []
        for (a, b, c, d, e) in self.cursor:
            res.append("{} | {} | {} | {} | {} was queried by 'author = {}'".format(a, b, c, d, e, value))
        return res

    def send_query(self, query):
        self.connect()
        self.cursor = self.cnx.cursor()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    def all_data(self):
        self.connect()
        query = "SELECT * FROM " + self.table + " LIMIT 80"
        data = pd.read_sql(
            query, self.cnx
        );
        return data
    
    def close(self):
        self.cursor.close()
        self.cnx.close()
    
    def workflow_step1(self, cond):
        strict_conditions = ""
        inspection_conditions = ""
        # score >
        
        already_started_condition = False
        
        if cond[0] and cond[0] is not None:
            already_started_condition = True
            strict_conditions = "WHERE score > " + str(cond[0])
            inspection_conditions = "WHERE score > " + str(max(cond[0] - 10, 0))
        # controversiality <
        if cond[1] and cond[1] is not None:
            if already_started_condition:
                strict_conditions += " AND controversiality < " + str(cond[1])
                inspection_conditions += " AND controversiality < " + str(cond[1])
            else:
                already_started_condition = True
                strict_conditions = "WHERE controversiality < " + str(cond[1])
                inspection_conditions = "WHERE controversiality < " + str(cond[1] + 2)
        # author =
        if cond[2] and cond[2] is not None and cond[2] != "":
            if already_started_condition:
                strict_conditions += " AND author = '" + cond[2] + "'"
                inspection_conditions += " AND author = '" + cond[2] + "'"
            else:
                already_started_condition = True
                strict_conditions = "WHERE author = '" + cond[2] + "'"
                inspection_conditions = "WHERE author = '" + cond[2] + "'"
        # partial text search in body
        if cond[3] and cond[3] is not None and cond[3] != "":
            a = '\"%'+ cond[3] + '%\"'
            if already_started_condition:
                strict_conditions += " AND body LIKE " + a
                inspection_conditions += " AND body LIKE " + a
            else:
                already_started_condition = True
                strict_conditions = "WHERE body LIKE " + a
                inspection_conditions = "WHERE body LIKE " + a
        
        try:
            self.connect()
            strict_query = "SELECT * FROM reddit_data " + strict_conditions + " LIMIT 80"
            inspection_query = "SELECT * FROM reddit_data " + inspection_conditions + " LIMIT 80"
            strict_data = pd.read_sql(
                strict_query, self.cnx
            )
            inspection_data = pd.read_sql(
                inspection_query, self.cnx
            )
            
            cond = inspection_data['id'].isin(strict_data['id'])
            inspection_data.drop(inspection_data[cond].index, inplace = True) # remove any duplicate rows
            
            time.sleep(3)
            return strict_data, inspection_data, True
        except Exception as ex:
            return None, None, False

    def workflow_step2(self, strict_data, inspection_data):
        try:
            res = strict_data.append(inspection_data)
            time.sleep(3)
            return res, True
        except Exception as ex:
            return None, False

    def workflow_step3(self, data, attributes, table):
        try:
            df = data[data.columns.intersection(attributes)]
            # df.to_sql only seems to support SQLAlchemy engines?
            engine = create_engine("mysql://cs511:databaesCS511@localhost/{db}".format(db=self.database))
            df.to_sql(table, engine, index=False, if_exists='replace') # convert to new table, drop the table if it exists already
            time.sleep(3)
            return df, True
        except Exception as ex:
            print(ex)
            return None, False

    def find_all_collections(self):
        self.connect()
        self.cursor = self.cnx.cursor()
        self.cursor.execute("show tables from " + self.database)
        rows = self.cursor.fetchall()
        return rows