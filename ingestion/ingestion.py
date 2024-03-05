import datetime
import hashlib

from flask import Flask, request, jsonify
import pandas as pd
from cassandra.cluster import Cluster

app = Flask(__name__)

# Cassandra database credentials
cassandra_keyspace = 'twitter_data'


# Function to connect to Cassandra database
def connect_to_cassandra():
    cluster = Cluster(contact_points=['cassandra-node1', 'cassandra-node2', 'cassandra-node3'], port=9042)
    # cluster = Cluster(contact_points=['cassandra-service.final-project'],port=9042)
    return cluster.connect(cassandra_keyspace)


# Function to insert tweet into Cassandra database
def insert_tweet_into_cassandra(tweet, session):
    insert_query = f"""
        INSERT INTO tweets 
            (id, tweet_id, author, country, content, language, number_of_likes, number_of_shares, date_time) 
        VALUES (%(id)s, %(tweet_id)s, %(author)s, %(country)s, %(content)s, %(language)s, %(number_of_likes)s, %(number_of_shares)s, %(date_time)s)
        """
    date_time_parse = datetime.datetime.strptime(tweet['date_time'], '%d/%m/%Y %H:%M')
    date_time_formatted = date_time_parse.strftime('%Y-%m-%d %H:%M:%S')

    # Generate deterministic UUID based on relevant fields
    id_content = f"{tweet['author']}_{tweet['content']}_{tweet['date_time']}"
    hashed_id = hashlib.md5(id_content.encode('utf-8')).hexdigest()

    data = {
        'id': hashed_id,
        'tweet_id': tweet['id'],
        'author': tweet['author'],
        'country': tweet['country'],
        'content': tweet['content'],
        'language': tweet['language'],
        'number_of_likes': tweet['number_of_likes'],
        'number_of_shares': tweet['number_of_shares'],
        'date_time': date_time_formatted
    }
    session.execute(insert_query, data)


# Main function for ingestion service
def ingest_tweets(csv_file_path, author_filter=None, content_filter=None):
    cluster = connect_to_cassandra()
    session = cluster

    try:

        # Read tweets from CSV file based on filters
        df = pd.read_csv(csv_file_path)
        df = df.replace({pd.NA: None})

        if author_filter:
            df = df[df['author'].str.contains(author_filter, case=False, na=False)]

        if content_filter:
            df = df[df['content'].str.contains(content_filter, case=False, na=False)]

        # Insert filtered tweets into Cassandra
        for _, tweet in df.iterrows():
            insert_tweet_into_cassandra(tweet, session)

        print("Ingestion completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        session.shutdown()


@app.route('/load_records', methods=['POST'])
def process_input():
    csv_file_path = 'data/tweets.csv'
    data = request.json
    # Add your processing logic here
    author_filter = data.get('author_filter', None)
    content_filter = data.get('content_filter', None)

    ingest_tweets(csv_file_path, author_filter, content_filter)

    result = {'message': 'Processed successfully'}
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
