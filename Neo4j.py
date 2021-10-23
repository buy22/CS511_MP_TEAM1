from neo4j import GraphDatabase
# import logging
# from neo4j.exceptions import ServiceUnavailable


# Aura queries use an encrypted connection using the "neo4j+s" URI scheme
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456"
driver = GraphDatabase.driver(uri, auth=(user, password))
session=driver.session()
#connnection testing
session.run("Match () Return 1 Limit 1")

# ql='''
# call apoc.load.json('sample_data.json')  yield value
# unwind value as v
# merge (:Reddit{id:v.id}) on create set reddit.permanentlink=v.permalink, reddit.body=v.body, reddit.distinguished=v.distinguished,reddit.score=v.score,reddit.stickied=v.stickied,reddit.retrieved_on=v.retrieved_on,reddit.can_gild=v.can_gild,reddit.controversiality=v.controversiality,reddit.edited=v.edited, reddit.body=v.body, reddit.author_flair_text=v.author_flair_text, reddit.created_utc=v.created_utc, reddit.gilded=v.gilded,reddit.author_flair_css_class=v.author_flair_css_class,reddit.link_id=v.link_id
# merge (a:Author {name:v.author})
# merge (s:SubReddit {name:v.subreddit_id}) on create set subreddit.subreddit=v.subreddit
# merge (smtr:IsSubmitter {relationship:v.is_submitter})
# merge (p:ParentID{id:parent_id})
# merge (a)-[:write]->(reddit)
# merge (s)-[:subreddit]->(reddit)
# '''
ql='''
call apoc.load.json('sample_data.json')  yield value
unwind value as v
merge (reddit:Reddit{id:v.id}) on create set reddit.permanentlink=v.permalink, reddit.body=v.body, reddit.distinguished=v.distinguished,reddit.score=v.score,reddit.stickied=v.stickied,reddit.retrieved_on=v.retrieved_on,reddit.can_gild=v.can_gild,reddit.controversiality=v.controversiality,reddit.edited=v.edited, reddit.body=v.body, reddit.author_flair_text=v.author_flair_text, reddit.created_utc=v.created_utc, reddit.gilded=v.gilded,reddit.author_flair_css_class=v.author_flair_css_class,reddit.link_id=v.link_id
merge (author:Author {name:v.author})
merge (subreddit:SubReddit {name:v.subreddit_id}) on create set subreddit.subreddit=v.subreddit
merge (issubmmiter:IsSubmitter {relationship:v.is_submitter})
merge (parentreddit:ParentReddit{id:v.parent_id})
merge (a)-[:write]->(reddit)
merge (s)-[:subreddit]->(reddit)
'''
#import data
result=session.run(ql).data()

session.close()







