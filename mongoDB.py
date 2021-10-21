from pymongo import MongoClient
import pandas as pd
client = MongoClient("localhost", 27017, maxPoolSize=50)
db = client.mp_team1
collection = db.test_table1
data = pd.DataFrame(list(collection.find()))

print(data)