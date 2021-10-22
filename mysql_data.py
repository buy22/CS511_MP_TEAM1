import json
import MySQLdb

# change user and password to match your MySQL user + password
USER = 'cs511'
PASS = 'databaesCS511'

mydb = MySQLdb.connect(host = "localhost",
					   user = USER,
					   passwd = PASS,
					   db = "team1",
                       charset="utf8mb4")

cursor = mydb.cursor()

print("Started Reading JSON file which contains multiple JSON document")

with open('sample_data.json') as f:
    for jsonObj in f:
        file_data = json.loads(jsonObj)
        
        # THIS DOES NOT COPY ALL THE JSON REDDIT DATA
        # some of it does not seem useful, but we can
        # redo this to add missing columns in if we think it will help
        author = file_data['author']
        body = file_data['body'] # should we remove whitespace in the body? Hmm
        controversiality = file_data['controversiality']
        user_id = file_data['id']
        score = file_data['score']
        subreddit = file_data['subreddit']
        subreddit_id = file_data['subreddit_id']
        
        # the Primary key (id) auto_increments so we don't need to worry about its value, passing in NULL will make it auto_inc.
        # I don't think it suffices to use anything else as a PK (some users post more than once so user_id and author wouldn't work)
        cursor.execute("INSERT INTO reddit_data (id, author, body, controversiality, user_id, score, subreddit, subreddit_id) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s)", (author, body, int(controversiality), user_id, int(score), subreddit, subreddit_id))

mydb.commit()
cursor.close()
print("Done")