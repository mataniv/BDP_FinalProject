from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
#INGESTION_SERVICE_URL = 'http://localhost:5001'
#BACKEND_SERVICE_URL = 'http://localhost:5002'
#POST_SERVICE_URL = 'http://localhost:5003'

INGESTION_SERVICE_URL = 'http://ingestion-container:5001'
BACKEND_SERVICE_URL = 'http://backend-container:5002'
POST_SERVICE_URL = 'http://post-container:5003'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/services', methods=['POST'])
def services():
    data = request.json

    # Test Ingestion Service
    ingestion_response = requests.post(f'{INGESTION_SERVICE_URL}/load_records', json=data)

    # Test Backend Service
    backend_response = requests.post(f'{BACKEND_SERVICE_URL}/run_query', json=data)

    # Test Post Service
    post_service_response = requests.post(f'{POST_SERVICE_URL}/request_tweet_pin')

    return jsonify({
        'ingestion_response': ingestion_response.text,
        'backend_response': backend_response.text,
        'post_service_response': post_service_response.json()
    })


@app.route('/post_tweet', methods=['POST'])
def post_tweet():
    data = request.form
    response = requests.post(f'{POST_SERVICE_URL}/post_tweet', data=data)
    return response.text


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
