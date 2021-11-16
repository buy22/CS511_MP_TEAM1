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
        self.inspect_data = None
        self.all = None
        self.db = db

    def to_list(self):
        return [self.id, self.db, self.name, self.conditions[0], self.conditions[1],
                self.conditions[2], self.conditions[3]]
