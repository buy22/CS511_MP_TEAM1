class Workflow:
    def __init__(self, id, name, schedule=None, conditions=[]):
        self.id = id
        self.name = name
        self.schedule = schedule
        self.conditions = conditions
        for i, j in enumerate(conditions):
            if j:
                if i == 0 or i == 1:
                    assert int(j) > 0
                    self.conditions[i] = int(j)

    def __str__(self):
        return 'Workflow - id: {}, name: {}, schedule: {}, condition: {}'.format(
            str(self.id), self.name, self.schedule, self.conditions)

