from pymongo import MongoClient
import pandas as pd
import time


class MongoDB:
    def __init__(self, db, collection=None):
        self.client = MongoClient("localhost", 27017, maxPoolSize=50)
        self.db = self.client[db]
        if collection:
            self.collection = self.db[collection]
        else:
            self.collection = None

    def find_all_collections(self):
        return [collection for collection in self.db.collection_names()]

    def all_data(self):
        # data = pd.DataFrame(list(self.collection.find()))
        show = {"_id": 0, "author_flair_text": 0, "author_flair_css_class": 0, "distinguished": 0, "id": 0,
                "can_gild": 0, "gilded": 0, "is_submitter": 0, "link_id": 0, "stickied": 0}
        data = pd.DataFrame(list(self.collection.find({}, show).limit(20)))
        return data

    def workflow_step1(self, cond):
        strict_conditions = {}
        inspection_conditions = {}
        # score >
        if cond[0]:
            strict_conditions["score"] = {"$gt": cond[0]}
            inspection_conditions["score"] = {"$gt": max(cond[0]-10, 0)}
        # controversiality <
        if cond[1]:
            strict_conditions["controversiality"] = {"lt": cond[1]}
            inspection_conditions["controversiality"] = {"lt": cond[1]}
        # author =
        if cond[2]:
            strict_conditions["author"] = {cond[2]}
            inspection_conditions["author"] = {cond[2]}
        # partial text search in body
        if cond[3]:
            self.collection.create_index([('body', 'text')])
            a = '\"' + cond[3] + '\"'
            strict_conditions["$text"] = {"$search": a}
            inspection_conditions["$text"] = {"$search": a}

        show = {"_id": 0, "author_flair_text": 0, "author_flair_css_class": 0, "distinguished": 0, "id": 0,
                "can_gild": 0, "gilded": 0, "is_submitter": 0, "link_id": 0, "stickied": 0}
        try:
            strict_data = pd.DataFrame(
                list(self.collection.find(strict_conditions, show).limit(20)))
            inspection_data = pd.DataFrame(
                list(self.collection.find(inspection_conditions, show).limit(20)))
            time.sleep(3)
            return strict_data, inspection_data, True
        except Exception as ex:
            return None, None, False

    def workflow_step2(self, strict_data, inspection_data):
        try:
            res = strict_data.append(inspection_data)
            time.sleep(3)
            return res, True
        except Exception as ex:
            return None, False

    def workflow_step3(self, data, attributes, table):
        try:
            df = data[data.columns.intersection(attributes)]
            collection = self.db[table]
            print(df)
            x = collection.insert_many(df.to_dict('records'))
            time.sleep(3)
            return df, True
        except Exception as ex:
            return None, False


