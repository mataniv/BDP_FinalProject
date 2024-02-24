CREATE KEYSPACE IF NOT EXISTS twitter_data
WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3};
USE twitter_data;

CREATE TABLE IF NOT EXISTS tweets (
    id TEXT PRIMARY KEY,
    tweet_id DECIMAL,
    author TEXT,
    country TEXT,
    content TEXT,
    language TEXT,
    number_of_likes INT,
    number_of_shares INT,
    date_time TIMESTAMP);

