import datetime
import numpy as np
from flask import Flask, request, jsonify
import pandas as pd
import mysql.connector

app = Flask(__name__)

# MySQL database credentials
# mysql_host = 'mysql-service'  # Replace with your MySQL service name in Kubernetes
mysql_host = 'localhost'  # Replace with your MySQL service name in Kubernetes
mysql_user = 'root'
mysql_password = 'root'
mysql_database = 'twitter_data'


# Function to connect to MySQL database
def connect_to_mysql():
    return mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)


# Function to create tweets table if not exists
def create_tweets_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tweets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tweet_id BIGINT, 
        author VARCHAR(255),
        country VARCHAR(255),
        content TEXT, 
        language VARCHAR(10),
        latitude DECIMAL(10, 6),
        longitude DECIMAL(10, 6),
        number_of_likes INT,
        number_of_shares INT,
        date_time DATETIME)
        """)
    cursor.execute("TRUNCATE TABLE tweets")


# Function to insert tweet into MySQL database
def insert_tweet_into_mysql(tweet, cursor):
    query = """
            INSERT INTO tweets 
                (tweet_id, author, country, content, language, latitude, longitude, number_of_likes, number_of_shares, date_time) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
    date_time = tweet['date_time']
    date_time_parse = datetime.datetime.strptime(date_time, '%d/%m/%Y %H:%M')
    date_time_formatted = date_time_parse.strftime('%Y-%m-%d %H:%M:%S')

    data = (tweet['id'], tweet['author'], tweet['country'], tweet['content'], tweet['language'], tweet['latitude'],
            tweet['longitude'], tweet['number_of_likes'], tweet['number_of_likes'], date_time_formatted)
    cursor.execute(query, data)


# Main function for ingestion service
def ingest_tweets(csv_file_path, content_filter):
    db_connection = connect_to_mysql()
    cursor = db_connection.cursor()

    try:

        # Create tweets table if not exists
        create_tweets_table(cursor)

        # Read tweets from CSV file based on filters
        df = pd.read_csv(csv_file_path)
        df = df.replace({np.nan: None})
        if content_filter:
            filtered_tweets = df[df['content'].str.contains(content_filter, case=False, na=False)]
        else:
            filtered_tweets = df

        # Insert filtered tweets into MySQL
        for _, tweet in filtered_tweets.iterrows():
            insert_tweet_into_mysql(tweet, cursor)

        db_connection.commit()
        print("Ingestion completed successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        cursor.close()
        db_connection.close()


@app.route('/process_input', methods=['POST'])
def process_input():
    csv_file_path = 'data/tweets.csv'
    data = request.json
    # Add your processing logic here
    if 'content_filter' in data.keys():
        ingest_tweets(csv_file_path, data['content_filter'])
    else:
        ingest_tweets(csv_file_path, '')
    result = {'message': 'Processed successfully'}
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
    # curl -d '{"content_filter":"Israel"}' -H "Content-Type: application/json" -X POST http://localhost:5001/process_input
