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
        show = {"_id": 0, "author_flair_text": 0, "author_flair_css_class": 0, "distinguished": 0,
                "can_gild": 0, "gilded": 0, "is_submitter": 0, "link_id": 0, "stickied": 0, 'author_cakeday': 0}
        data = pd.DataFrame(list(self.collection.find({}, show).limit(80)))
        return data

    def workflow_step1(self, cond):
        strict_conditions = {}
        inspection_conditions = {}
        # score >
        if cond[0] is not None:
            strict_conditions["score"] = {"$gt": cond[0]}
            inspection_conditions["score"] = {"$gt": max(cond[0]-10, 0)}
        # controversiality <
        if cond[1] is not None:
            strict_conditions["controversiality"] = {"lt": cond[1]}
            inspection_conditions["controversiality"] = {"lt": cond[1]}
        # author =
        if cond[2] is not None:
            strict_conditions["author"] = {"$regex": cond[2]}
            inspection_conditions["author"] = {"$regex": cond[2]}
        # partial text search in body
        if cond[3] is not None:
            self.collection.create_index([('body', 'text')])
            a = '.*' + cond[3] + '.*'
            strict_conditions['body'] = {"$regex": a}
            inspection_conditions['body'] = {"$regex": a}
        show = {"_id": 0, "author_flair_text": 0, "author_flair_css_class": 0, "distinguished": 0,
                "can_gild": 0, "gilded": 0, "is_submitter": 0, "link_id": 0, "stickied": 0, 'author_cakeday': 0}
        try:
            strict_data = pd.DataFrame(
                list(self.collection.find(strict_conditions, show).limit(20)))
            if not strict_data.empty:
                inspection_conditions["id"] = {"$nin": list(strict_data['id'])}
            inspection_data = pd.DataFrame(
                list(self.collection.find(inspection_conditions, show).limit(20)))
            time.sleep(3)
            return strict_data, inspection_data, True
        except Exception as ex:
            raise ex

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
            collection.drop()
            x = collection.insert_many(df.to_dict('records'))
            time.sleep(3)
            return df, True
        except Exception as ex:
            return None, False

    def get_keyword_reddit(self, keyword):
        # get reddit body data that contains keyword
        self.collection.create_index([('body', 'text')])
        condition = {'body': {"$regex": '.*' + keyword.lower() + '.*'}}
        show = {"_id": 0, "author_flair_text": 0, "author_flair_css_class": 0, "distinguished": 0,
                "can_gild": 0, "gilded": 0, "is_submitter": 0, "link_id": 0, "stickied": 0, 'author_cakeday': 0}
        data = pd.DataFrame(list(self.collection.find(condition, show)))
        df = data[data.columns.intersection(['body'])]
        # convert string to lower case
        body_df = df['body'].str.lower()
        return body_df
