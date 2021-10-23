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

    def workflow_step1(self, cond):
        try:
            strict_data = pd.DataFrame(list(self.collection.find({"score": {"$gt": cond[0]}},
                                                                 {"_id": 0}).limit(20)))
            inspection_data = pd.DataFrame(
                list(self.collection.find({"score": {"$gt": max(cond[0]-10, 0)}}, {"_id": 0}).limit(20)))
            return strict_data, inspection_data, True
        except Exception as ex:
            return None, None, False

    def workflow_step2(self, strict_data, inspection_data):
        try:
            strict_data.append(inspection_data)
            return strict_data, True
        except Exception as ex:
            return None, False

    def workflow_step3(self, data, attributes):
        try:
            df = data[data.columns.intersection(attributes)]
            return df, True
        except Exception as ex:
            return None, False


