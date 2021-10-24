from Mysql import Mysql
from mongoDB import MongoDB


class Workflow:
    def __init__(self, db, id, name, schedule=None, conditions=[], attributes=[], dependency=None):
        self.id = id
        self.name = name
        if schedule:
            assert int(schedule) > 0
            self.schedule = int(schedule)
        else:
            self.schedule = None
        self.conditions = conditions
        for i, j in enumerate(conditions):
            if j:
                if i == 0 or i == 1:
                    assert int(j) > 0
                    self.conditions[i] = int(j)
        self.dependency = dependency
        self.attributes = attributes
        self.db = db

    def __str__(self):
        return 'Workflow - id: {}, name: {}, schedule: {}, condition: {}'.format(
            str(self.id), self.name, self.schedule, self.conditions)
    
    def to_list(self):
        return [self.id, self.name, self.schedule, self.conditions[0], self.conditions[1], self.conditions[2], self.conditions[3]]

    def workflow_step1(self):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comment')
        else:
            return None
        return con.workflow_step1(self.conditions)

    def workflow_step2(self, strict_data, inspection_data):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comment')
        else:
            return None
        return con.workflow_step2(strict_data, inspection_data)

    def workflow_step3(self, data):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comment')
        else:
            return None
        return con.workflow_step3(data, self.attributes, 'workflow_'+str(self.id))
