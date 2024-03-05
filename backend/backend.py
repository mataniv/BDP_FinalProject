from flask import Flask, request, jsonify
from cassandra.cluster import Cluster

app = Flask(__name__)

# Cassandra database credentials
cassandra_keyspace = 'twitter_data'
cassandra_table = 'tweets'


# Function to connect to Cassandra database
def connect_to_cassandra():
    cluster = Cluster(contact_points=['cassandra-node1', 'cassandra-node2', 'cassandra-node3'], port=9042)
    # cluster = Cluster(contact_points=['cassandra-service.final-project'],port=9042)
    return cluster.connect(cassandra_keyspace)


# Function to execute a query against Cassandra database based on filters
def execute_cassandra_query_with_filters(filters, session):
    try:
        query = f"SELECT * FROM {cassandra_table}"

        conditions = []
        for column, value in filters.items():
            if value and column != 'content':
                conditions.append(f" {column} = '{value}'")

        if conditions:
            query += f" WHERE {' AND'.join(conditions)}"
            query += " ALLOW FILTERING"
            result = session.execute(query)
        else:
            result = session.execute(query)
        return result
    except Exception as e:
        print(f"Error executing query in cassandra: {str(e)}")
        return None


# Function to filter content in the result set
def filter_content(result_set, content_filter):
    filtered_rows = [
        row for row in result_set if content_filter.lower() in row['content'].lower()
    ]
    return filtered_rows


# API endpoint to run queries based on filters
@app.route('/run_query', methods=['POST'])
def run_query():
    try:
        data = request.json
        filters = data.get('filters', {})
        content_filter = filters.get('content', '').lower()

        if filters:
            # Connect to Cassandra
            session = connect_to_cassandra()

            # Execute the query based on filters
            result = execute_cassandra_query_with_filters(filters, session)

            # Convert result to JSON and filter content
            if result:
                json_result = [
                    {
                        'id': str(row.id),
                        'author': row.author,
                        'content': row.content,
                        'country': row.country,
                        'date_time': row.date_time.isoformat(),
                        'language': row.language,
                        'number_of_likes': row.number_of_likes,
                        'number_of_shares': row.number_of_shares,
                        'tweet_id': str(row.tweet_id)
                    }
                    for row in result
                ]

                if content_filter:
                    json_result = filter_content(json_result, content_filter)

                return jsonify({'result': json_result})
            else:
                return jsonify({'result': []})

        return jsonify({'error': 'Invalid request'})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
