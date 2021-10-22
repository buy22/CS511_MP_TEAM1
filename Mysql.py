import mysql.connector
import pandas as pd

class Mysql:
    def __init__(self, db):
        self.cnx = None
        self.cursor = None
        self.database = db

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
        data = pd.read_sql(
            "SELECT * FROM reddit_data LIMIT 20", self.cnx
        );
        return data
    
    def close(self):
        self.cursor.close()
        self.cnx.close()