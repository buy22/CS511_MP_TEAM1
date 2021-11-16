from Mysql import Mysql
from mongoDB import MongoDB
from Neo4j import Neo4j


class Subcomponent:
    def __init__(self, db, id, name, conditions=[], attributes=[]):
        self.id = id
        self.name = name
        self.conditions = conditions
        for i, j in enumerate(conditions):
            if j:
                if i == 0 or i == 1:
                    assert int(j) > 0
                    self.conditions[i] = int(j)
        self.attributes = attributes
        self.strict_data, self.inspect_data = None, None
        self.all = None
        self.db = db

    def to_list(self):
        return [self.id, self.db, self.name, self.conditions[0], self.conditions[1],
                self.conditions[2], self.conditions[3]]

    def retrieve_inspect_data(self, inspected):
        self.inspect_data = inspected

    def subcomponent_step1(self, scheduled=False):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comments')
        else:
            con = Neo4j('neo4j')
        res = con.workflow_step1(self.conditions)
        if scheduled:
            self.strict_data, _, _ = res
        else:
            self.strict_data, self.inspect_data, _ = res
        return res

    def subcomponent_step2(self, scheduled=False):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comments')
        else:
            con = Neo4j('neo4j')
        if scheduled:
            self.inspect_data = None
        self.all, success = con.workflow_step2(self.strict_data, self.inspect_data)
        return success

    def subcomponent_step3(self):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comments')
        else:
            con = Neo4j('neo4j')
        return con.workflow_step3(self.all, self.attributes, 'workflow_'+str(self.id))