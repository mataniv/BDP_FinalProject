from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/ingestion', methods=['GET', 'POST'])
def ingestion():
    if request.method == 'GET':
        return render_template('load-data.html')
    else:  # Handle the POST request from the ingestion page
        data = request.json
        response = requests.post('http://ingestion-container:5001/load_records', json=data)
        if response.status_code == 200:
            return jsonify({'message': 'Processed successfully.'}), 200
        else:
            return jsonify({'message': 'Failed loading.'}), 500

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    response = requests.post('http://backend-container:5002/run_query', json={'filters': data['filters']})
    if response.status_code == 200:
        results = response.json().get('result', [])
        if not results:
            return jsonify({'message': 'No results found.', 'result': []}), 200
        return jsonify(response.json()), 200
    else:
        return jsonify({'message': 'Error fetching results.'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)
