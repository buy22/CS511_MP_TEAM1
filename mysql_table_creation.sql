create database team1;
use team1;

create table reddit_data (
	id INT NOT NULL AUTO_INCREMENT,
    author VARCHAR(50),
    body VARCHAR(10000),
    controversiality INT,
    user_id VARCHAR(10),
    score INT,
    subreddit VARCHAR(25),
    subreddit_id VARCHAR(10),
    PRIMARY KEY(id)
);

select * from reddit_data;