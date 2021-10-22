from pymongo import MongoClient
import pandas as pd

class MongoDB:
    def __init__(self, db, collection):
        self.client = MongoClient("localhost", 27017, maxPoolSize=50)
        self.db = self.client[db]
        self.collection = self.db[collection]

    def all_data(self):
        # data = pd.DataFrame(list(self.collection.find()))
        data = pd.DataFrame(list(self.collection.find({}, {"_id": 0}).limit(20)))
        return data