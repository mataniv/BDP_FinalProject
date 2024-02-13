CREATE KEYSPACE IF NOT EXISTS twitter_data
WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3};
