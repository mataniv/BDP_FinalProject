import os
from flask import Flask, request, jsonify, redirect
from requests_oauthlib import OAuth1Session

app = Flask(__name__)


consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")

if not (consumer_key and consumer_secret):
    raise ValueError("Consumer key and secret must be provided as environment variables.")


@app.route('/request_tweet_pin', methods=['POST'])
def request_tweet_pin():
    try:
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
        fetch_response = oauth.fetch_request_token(
            "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write")
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")

        authorization_url = oauth.authorization_url("https://api.twitter.com/oauth/authorize")

        return jsonify({"oauth_token": resource_owner_key, "oauth_token_secret": resource_owner_secret,
                        "authorization_url": authorization_url})
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/post_tweet', methods=['POST'])
def post_tweet():
    try:
        oauth_token = request.form.get('oauth_token')
        oauth_token_secret = request.form.get('oauth_token_secret')
        verifier = request.form.get('verifier')
        tweet_text = request.form.get('tweet_text')

        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
            verifier=verifier,
        )

        oauth_tokens = oauth.fetch_access_token("https://api.twitter.com/oauth/access_token")
        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        response = oauth.post("https://api.twitter.com/2/tweets", json={"text": tweet_text})

        if response.status_code != 201:
            raise Exception(f"Error posting tweet: {response.status_code} - {response.text}")

        return jsonify({"status": "Tweet posted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5003)
