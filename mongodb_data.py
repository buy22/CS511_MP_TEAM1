import json
from pymongo import MongoClient

studentsList = []
print("Started Reading JSON file which contains multiple JSON document")
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client['mp_team1']
collection = db['comments']
with open('sample_data.json') as f:
    for jsonObj in f:
        file_data = json.loads(jsonObj)
        if isinstance(file_data, list):
            collection.insert_many(file_data)
        else:
            collection.insert_one(file_data)

print("Done")