# BIG DATA PLATFORM - Final Project / 2023

<img width="763" alt="image" src="https://github.com/mataniv/BDP_FinalProject/assets/38129502/79103152-6cc8-425c-9cdd-d0b728220810">

# First Step: Deploy the app locally using Docker

The following steps provide a quick guide on setting up and running the components of the project locally using Docker.

## Prerequisites
Make sure you have Docker installed on your machine.


## 1. Cassandra Cluster Setup
Create a Docker network for Cassandra:

    docker network create cassandra-net
    
Build and run the Cassandra cluster locally:


	cd cassandra
	docker volume create cassandra-node1-data
	docker volume create cassandra-node2-data
	docker volume create cassandra-node3-data
	
	# Run Cassandra nodes
	docker run --name cassandra-node1 --network cassandra-net \
	  -e CASSANDRA_CLUSTER_NAME=MyCluster \
	  -e CASSANDRA_SEEDS=cassandra-node1 \
	  -v cassandra-node1-data:/var/lib/cassandra \
	  -p 9042:9042 \
	  -d cassandra:latest

	docker run --name cassandra-node2 --network cassandra-net \
	  -e CASSANDRA_CLUSTER_NAME=MyCluster \
	  -e CASSANDRA_SEEDS=cassandra-node1 \
	  -v cassandra-node2-data:/var/lib/cassandra \
	  -p 9043:9042 \
	  -d cassandra:latest

	docker run --name cassandra-node3 --network cassandra-net \
	  -e CASSANDRA_CLUSTER_NAME=MyCluster \
	  -e CASSANDRA_SEEDS=cassandra-node1 \
	  -v cassandra-node3-data:/var/lib/cassandra \
	  -p 9044:9042 \
	  -d cassandra:latest

	# Copy and execute database schema creation script
	docker cp create_database.cql cassandra-node1:/create_database.cql
	docker exec -it cassandra-node1 cqlsh -f /create_database.cql

## 2. Build and Run Ingestion Service
	cd ingestion
	docker build -t ingestion_image .
	docker run -p 5001:5001 -d --network cassandra-net --name ingestion-container ingestion_image

## 3. Build and Run Backend Service

	cd backend
	docker build -t backend_image .
	docker run -p 5002:5002 -d --network cassandra-net --name backend-container backend_image

## 4. Test Ingestion and Backend Endpoints
	# Test ingestion endpoint
	curl -d '{"content_filter":"germany"}' -H "Content-Type: application/json" -X POST http://localhost:5001/load_records
	curl -d '{"author_filter":"britneyspears"}' -H "Content-Type: application/json" -X POST http://localhost:5001/load_records
	curl -d '{"content_filter":"light","author_filter":"katyperry"}' -H "Content-Type: application/json" -X POST http://localhost:5001/load_records

	# Test backend endpoint
	curl -d '{"filters":{"author":"britneyspears"}}' -H "Content-Type: application/json" -X POST http://localhost:5002/run_query
	curl -d '{"filters":{"content":"germany"}}' -H "Content-Type: application/json" -X POST http://localhost:5002/run_query
	curl -d '{"filters":{"language":"es"}}' -H "Content-Type: application/json" -X POST http://localhost:5002/run_query
	curl -d '{"filters":{"content":"blalba"}}' -H "Content-Type: application/json" -X POST http://localhost:5002/run_query


## 5. Build and Run Post Service
	cd post
	docker build -t post_image .
	docker run -p 5003:5003 -d --network cassandra-net -e CONSUMER_KEY="<consumer_key>" -e CONSUMER_SECRET="<consumer_secret>" --name post-container post_image


## 6. Test Post Service
	curl -X POST http://localhost:5003/request_tweet_pin

	# Response example:
	# {
	#   "authorization_url": "https://api.twitter.com/oauth/authorize?oauth_token=S-xJWgAAAAABsTelAAABjc0-MoI",
	#   "oauth_token": "S-xJWgAAAAABsTelAAABjc0-MoI",
	#   "oauth_token_secret": "8JxhdJh4BieWRcpkGnVAjGL2Y8X8G5uk"
	# }

	curl -X POST -d "oauth_token=S-xJWgAAAAABsTelAAABjc0-MoI&oauth_token_secret=8JxhdJh4BieWRcpkGnVAjGL2Y8X8G5uk&verifier=8148937&tweet_text=Hello Twitter" http://localhost:5009/post_tweet

## 7. Build and Run UI App

	cd ui_app
	docker build -t bdp_ui_app .
	docker run -p 5005:5005 -d --network cassandra-net -e OAUTH_TOKEN="<oauth_token>" -e OAUTH_TOKEN_SECRET="<oauth_token_secret>" -e VERIFIER="<verifier>" --name flask-search-app-container bdp_ui_app

Now, your project components are up and running locally. Access the UI app at http://localhost:5005 to interact with the system.
