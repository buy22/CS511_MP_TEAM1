import pandas as pd
from Mysql import Mysql
from mongoDB import MongoDB
from Neo4j import Neo4j
from apps import create_subcomponents


class Workflow:
    def __init__(self, id, name, subcomponents=[], schedule=None, status="Idle", dependency=None):
        self.id = id
        self.name = name
        self.subcomponents = subcomponents
        if schedule:
            assert int(schedule) > 0
            self.schedule = int(schedule)
        else:
            self.schedule = None
        self.status = status
        self.dependency = dependency
        self.wait_time = schedule
    
    def to_list(self):
        return [self.id, self.name, self.schedule, ','.join([str(i) for i in self.subcomponents]), self.status, str(self.dependency)]

    def workflow_step1(self, scheduled=False):
        s = True
        for i in self.subcomponents:
            s = create_subcomponents.subcomponents[i]
            _, _, success = s.subcomponent_step1(scheduled)
            s = s and success
        return s

    def workflow_step2(self, scheduled=False):
        s = True
        for i in self.subcomponents:
            s = create_subcomponents.subcomponents[i]
            success = s.subcomponent_step2(scheduled)
            s = s and success
        return s

    def workflow_step3(self):
        for i in self.subcomponents:
            s = create_subcomponents.subcomponents[i]
            _, success = s.subcomponent_step3(self.id)
        return True
