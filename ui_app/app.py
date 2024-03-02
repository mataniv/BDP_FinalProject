from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
from io import StringIO

# Initialize the Flask application
app = Flask(__name__)

@app.route('/chart-data')
def chart_data():
    """
    This route handles the request for chart data. It makes a POST request to the backend service,
    processes the data returned, and sends back a JSON response with data for tweets by year and
    top authors, to be used in the frontend charts.
    """
    response = requests.post('http://backend-container:5002/run_query', json={"filters": {"content": ""}})
    if response.status_code == 200:
        data = response.json().get('result', [])
        df = pd.DataFrame(data)
        df['date_time'] = pd.to_datetime(df['date_time'])
        tweets_by_year = df['date_time'].dt.year.value_counts().sort_index().to_dict()
        top_authors = df['author'].value_counts().nlargest(5).reset_index().rename(
            columns={'index': 'name', 'author': 'tweetCount'}).to_dict(orient='records')
        return jsonify(tweets_by_year=tweets_by_year, top_authors=top_authors)
    else:
        return jsonify({'error': 'Failed to fetch data'}), response.status_code

@app.route('/post_tweet', methods=['GET', 'POST'])
def post_tweet():
    if request.method == 'POST':
        oauth_token = 'your_oauth_token'
        oauth_token_secret = 'your_oauth_token_secret'
        verifier = 'your_verifier'
        tweet_text = request.form.get('tweet_text')

        data = {
            "oauth_token": oauth_token,
            "oauth_token_secret": oauth_token_secret,
            "verifier": verifier,
            "tweet_text": tweet_text
        }

        response = requests.post('http://post-container:5003/post_tweet', data=data)
        if response.status_code == 200:
            return jsonify({'message': 'Processed successfully.'})
        else:
            return jsonify({'message': 'Failed loading.'}), response.status_code

    return render_template('tweet.html')


@app.route('/')
def home():
    """
    The root route that serves the main HTML page of the application.
    """
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    """
    This route serves the analytics HTML page that includes the analytics dashboard.
    """
    return render_template('analytics.html')

@app.route('/ingestion', methods=['GET', 'POST'])
def ingestion():
    if request.method == 'POST':
        data = request.get_json()
        # Make sure to use request.get_json() to parse JSON data correctly

        response = requests.post('http://ingestion-container:5001/load_records', json=data)
        if response.status_code == 200:
            return jsonify({'message': 'Processed successfully.'}), 200
        else:
            return jsonify({'message': 'Failed loading.'}), response.status_code

    return render_template('load-data.html')

@app.route('/search', methods=['POST'])
def search():
    """
    This POST route handles the search functionality by forwarding the search queries
    to the backend service and returning the results.
    """
    data = request.json
    response = requests.post('http://backend-container:5002/run_query', json={'filters': data['filters']})
    if response.status_code == 200:
        results = response.json().get('result', [])
        if not results:
            return jsonify({'message': 'No results found.', 'result': []}), 200
        return jsonify(response.json()), 200
    else:
        return jsonify({'message': 'Error fetching results.'}), 500

# Start the Flask development server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)
