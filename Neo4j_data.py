from neo4j import GraphDatabase
# import logging
# from neo4j.exceptions import ServiceUnavailable


# Aura queries use an encrypted connection using the "neo4j+s" URI scheme
uri = "bolt://localhost:7687"
user = "neo4j"
password = "123456"
driver = GraphDatabase.driver(uri, auth=(user, password))
session=driver.session(database='neo4j')
#connnection testing
session.run("Match () Return 1 Limit 1")

#clear all data
ql='''
MATCH (n)
DETACH DELETE n
'''
session.run(ql)

#import data
ql='''
call apoc.load.json('sample_data.json')  yield value
unwind value as v
merge (reddit:Reddit{redditID:v.id}) on create set reddit.body=v.body,reddit.score=v.score,reddit.controversiality=v.controversiality,reddit.edited=v.edited,
reddit.permanentlink=v.permalink, reddit.distinguished=v.distinguished,reddit.stickied=v.stickied,  reddit.link_id=v.link_i
// reddit.can_gild=v.can_gild, reddit.gilded=v.gilded,
// reddit.retrieved_on=v.retrieved_on,reddit.created_utc=v.created_utc,
merge (author:Author {name:v.author}) on create set author.author_flair_text=v.author_flair_text,author.author_flair_css_class=v.author_flair_css_class
merge (author)-[:Author]->(reddit)

merge (subreddit:SubReddit {subredditID:v.subreddit_id}) on create set subreddit.subreddit=v.subreddit
merge (subreddit)-[:subreddit]->(reddit)

// foreach()

// merge (issubmmiter:IsSubmitter {relationship:v.is_submitter})
// merge (parentreddit:ParentReddit{id:v.parent_id})
'''
result=session.run(ql).data()

session.close()