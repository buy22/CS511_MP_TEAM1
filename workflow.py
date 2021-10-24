from Mysql import Mysql
from mongoDB import MongoDB


class Workflow:
    def __init__(self, db, id, name, schedule=None, status="Idle", conditions=[], attributes=[],
                 dependency=None, strict_data=None):
        self.id = id
        self.name = name
        if schedule:
            assert int(schedule) > 0
            self.schedule = int(schedule)
        else:
            self.schedule = None
        self.status = status
        self.conditions = conditions
        for i, j in enumerate(conditions):
            if j:
                if i == 0 or i == 1:
                    assert int(j) > 0
                    self.conditions[i] = int(j)
        self.dependency = dependency
        self.attributes = attributes
        self.strict_data = strict_data
        self.inspect_data = None
        self.all = None
        self.db = db
        self.wait_time = schedule

    def __str__(self):
        return 'Workflow - id: {}, name: {}, schedule: {}, condition: {}, attributes: {}, dependency: {}'.format(
            str(self.id), self.name, self.schedule, self.conditions, self.attributes, self.dependency)
    
    def to_list(self):
        return [self.id, self.db, self.name, self.schedule, self.status, self.conditions[0], self.conditions[1],
                self.conditions[2], self.conditions[3], str(self.dependency)]

    def retrieve_inspect_data(self, inspected):
        self.inspect_data = inspected

    def workflow_step1(self, scheduled=False):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comments')
        else:
            return None
        res = con.workflow_step1(self.conditions)
        if scheduled:
            self.strict_data, _, _ = res
        else:
            self.strict_data, self.inspect_data, _ = res
        return res

    def workflow_step2(self, scheduled=False):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comments')
        else:
            return None
        if scheduled:
            self.inspect_data = None
        self.all, success = con.workflow_step2(self.strict_data, self.inspect_data)
        return success

    def workflow_step3(self):
        if self.db == 'MySQL':
            con = Mysql('team1', 'reddit_data')
        elif self.db == 'MongoDB':
            con = MongoDB('mp_team1', 'comments')
        else:
            return None
        return con.workflow_step3(self.all, self.attributes, 'workflow_'+str(self.id))
