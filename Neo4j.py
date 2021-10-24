from neo4j import GraphDatabase
import pandas as pd
import time

class Neo4j:
    def __init__(self,db):
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "123456"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = self.driver.session(database=db)

    def close(self):
        self.session.close()

    def all_data(self):
        query = "MATCH (m:Author)-[:Author]->(n:Reddit) RETURN n.body,n.score,n.controversiality,m.name LIMIT 25"
        data=pd.DataFrame(self.session.run(query).data())
        return data

    def workflow_step1(self, cond):
        strict_conditions = ""
        inspection_conditions = ""

        already_started_condition = False
        # score >
        if str(cond[0]) and cond[0] is not None:
            already_started_condition = True
            strict_conditions = "WHERE n.score > " + str(cond[0])
            inspection_conditions = "WHERE n.score > " + str(max(cond[0] - 10, 0))
        # controversiality =
        if str(cond[1]) and cond[1] is not None:
            if already_started_condition:
                strict_conditions += " AND n.controversiality = " + str(cond[1])
                inspection_conditions += ""
            else:
                already_started_condition = True
                strict_conditions = "WHERE n.controversiality = " + str(cond[1])
                inspection_conditions = "WHERE "
        # author =
        if cond[2] and cond[2] is not None and cond[2] != "":
            if already_started_condition:
                strict_conditions += " AND m.name = '" + cond[2] + "'"
                inspection_conditions += " AND m.name = '" + cond[2] + "'"
            else:
                already_started_condition = True
                strict_conditions = "WHERE m.name = '" + cond[2] + "'"
                inspection_conditions = "WHERE m.name = '" + cond[2] + "'"
        # partial text search in body
        if cond[3] and cond[3] is not None and cond[3] != "":
            if already_started_condition:
                strict_conditions += " AND n.body CONTAINS '" + cond[3] + "'"
                inspection_conditions += " AND n.body CONTAINS '" + cond[3] + "'"
            else:
                already_started_condition = True
                strict_conditions = "WHERE n.body CONTAINS '" + cond[3] + "'"
                inspection_conditions = "WHERE n.body CONTAINS '" + cond[3] + "'"

        try:
            strict_query = "MATCH (m:Author)-[:Author]->(n:Reddit) " + strict_conditions + " RETURN n,m LIMIT 20"
            inspection_query = "MATCH (m:Author)-[:Author]->(n:Reddit) " + inspection_conditions + " RETURN n,m LIMIT 20"
            print(strict_query)
            print(inspection_query)
            print(self.session.run(strict_query).data())
            strict_data = pd.DataFrame(self.session.run(strict_query).data())
            inspection_data = pd.DataFrame(self.session.run(inspection_query).data())
            time.sleep(3)
            return strict_data, inspection_data, True
        except Exception as ex:
            return None, None, False

    def workflow_step2(self, strict_data, inspection_data):
        try:
            strict_data.append(inspection_data)
            time.sleep(3)
            return strict_data, True
        except Exception as ex:
            return None, False

    def workflow_step3(self, data, attributes, table):
        try:
            df = data[data.columns.intersection(attributes)]
            collection = self.db[table]
            x = collection.insert_many(df.to_dict('records'))
            time.sleep(3)
            return df, True
        except Exception as ex:
            return None, False

    def find_all_collections(self):
        pass

