import mysql.connector


class Mysql:
    def __init__(self):
        self.cnx = None
        self.cursor = None

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(user='root', password='your password here',
                                               host='127.0.0.1', database='MP_team1')
        except Exception as ex:
            raise ex

    def query_test1(self, value):
        self.cursor = self.cnx.cursor()
        query = ("SELECT * FROM test1 "
                 "HAVING author = {}".format(value))
        self.cursor.execute(query)
        res = []
        for (a, b, c, d, e) in self.cursor:
            res.append("{} | {} | {} | {} | {} was queried by 'author = {}'".format(a, b, c, d, e, value))
        return res

    def close(self):
        self.cursor.close()
        self.cnx.close()

