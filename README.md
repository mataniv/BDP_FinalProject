# BIG DATA PLATFORM - Final Project / 2023
## Project Overview


<img width="763" alt="image" src="https://github.com/mataniv/BDP_FinalProject/assets/38129502/79103152-6cc8-425c-9cdd-d0b728220810">

&nbsp;

| Service |Purpose  |Input |Output  |
|--|--|--|--|
|**Ingestion Service**|Recieve requests for ingestion by the UI application.| filter (by author or content)|Insert records to the database|
|**Cassandra Cluster**|A persistence database for the application|Queries & Insertions| Table records|
|**Backend**|A backend service for the UI application |Requests to retrieve tweets|Return records to the UI application|
|**Post Service**|Submit a tweet to the Twitter platform using the API|Text|A tweet on Twitter|
|**UI App**|Present insights visually and empower users to ingest tweets into the system|Users have the capability to request information retrieval based on content or author, and additionally, they can post tweets|insights|

## Prerequisites
Make sure you have installed the following apps:
1. Docker
2. Minikube

Clone the repository:

	git clone https://github.com/mataniv/BDP_FinalProject.git

# First Step: Deploy the app locally using Docker

The following steps provide a quick guide on setting up and running the components of the project locally using Docker.

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

# Deploy Application Into Minikube Cluster

## 1. Configure Codebase Based on Our Kubernetes Services

	cp -r backend minikube_backend
	cp -r ingestion minikube_ingestion
	cp -r ui_app minikube_ui_app

 Replace the lines in the following files:

 `minikube_backend/backend.py`:

	cluster = Cluster(contact_points=['cassandra-node1','cassandra-node2','cassandra-node3'],port=9042)
	# cluster = Cluster(contact_points=['cassandra-service.final-project'],port=9042)

`minikube_ingestion/ingestion.py`:

	cluster = Cluster(contact_points=['cassandra-node1', 'cassandra-node2', 'cassandra-node3'], port=9042)
	# cluster = Cluster(contact_points=['cassandra-service.final-project'],port=9042)

`minikube_ui_app/app.py`:

	 response = requests.post('http://backend-container:5002/run_query', json={"filters": {"content": ""}})
	 # response = requests.post('http://backend-service.final-project:5002/run_query', json={"filters": {"content": ""}})
	
	 response = requests.post('http://post-container:5003/post_tweet', data=data)
	 # response = requests.post('http://post-service.final-project:5003/post_tweet', data=data)
	
	 response = requests.post('http://ingestion-container:5001/load_records', json=data)
	 # response = requests.post('http://ingestion-service.final-project:5001/load_records', json=data)
	
	 response = requests.post('http://backend-container:5002/run_query', json={'filters': data['filters']})
	 # response = requests.post('http://backend-service.final-project:5002/run_query', json={'filters': data['filters']})

## 2. Prepare Docker Images

In the BDP_FinalProject directory Run the following commands to prepare docker images
with specific tag names.

	docker build -t matanniv01/backend-service:v1.3 ./minikube_backend
	docker build -t matanniv01/ingestion-service:v1.3 ./minikube_ingestion
	docker build -t matanniv01/post-service:v1.3 ./post
	docker build -t matanniv01/frontend-service:v1.3 ./minikube_ui_app

 Now we push the docker images into Docker Hub:

	docker login
	docker push matanniv01/backend-service:v1.3
	docker push matanniv01/ingestion-service:v1.3
	docker push matanniv01/post-service:v1.3
	docker push matanniv01/frontend-service:v1.3

 The necessary yml files can be found in the `minikube` directory:
 
```console
 minikube/
├── backend.yml
├── cassandra-pv.yml
├── cassandra.yml
├── frontend.yml
├── ingestion.yml
├── ingress.yml
└── post.yml
```

## 3. Deploy Application Into Minikube Cluster

	minikube start
	alias kubectl="minikube kubectl --"
 
Simply run the below command, and your application will be seamlessly added to the
Kubernetes Minikube cluster, ready to leverage its robust orchestration capabilities for
deployment, scaling, and management.

	kubectl create secret generic post-secrets --from-literal=CONSUMER_KEY='your_consumer_key' \
	        --from-literal=CONSUMER_SECRET='your_consumer_secret' \
	        -n final-project

&nbsp;

	kubectl create secret generic frontend-secrets --from-literal=OAUTH_TOKEN='your_oauth_token' \
		--from-literal=OAUTH_TOKEN_SECRET='your_oauth_token_secret' \
		--from-literal=VERIFIER='your_verifier' -n final-project

&nbsp;

	kubectl create namespace final-project
	kubectl apply -f minikube/backend.yml
	kubectl apply -f minikube/frontend.yml
	kubectl apply -f minikube/post.yml
	kubectl apply -f minikube/ingestion.yml
	kubectl apply -f minikube/cassandra-pv.yml
	kubectl apply -f minikube/cassandra.yml
	minikube addons enable ingress
	kubectl apply -f minikube/ingress.yml

To check that all services are running:

	kubectl get pods -n final-project
 
```console
NAME                                    READY   STATUS    RESTARTS   AGE
backend-deployment-67fcdbf7bc-qb92l     1/1     Running   0          2m39s
cassandra-0                             1/1     Running   0          2m20s
ingestion-deployment-85f9f69476-ptff8   1/1     Running   0          2m26s
post-deployment-79bb4d8b44-9kgsf        1/1     Running   0          2m30s
ui-deployment-5d965f954d-6xnqw          1/1     Running   0          2m34s
```

Run this command to check the ingress controller:

	kubectl get ingress -n final-project

 ```console
NAME         CLASS   HOSTS   ADDRESS        PORTS   AGE
ui-ingress   nginx   *       192.168.49.2   80      2m15s
```

You can notice that our ingress service is running.

## 5. Setup Cassandra Database

To setup cassandra database into cluster we need to run this following commands.

	kubectl cp cassandra/create_database.cql final-project/cassandra-0:/create_database.cql
 	kubectl exec -it cassandra-0 -n final-project -- /bin/bash -c "cqlsh -f /create_database.cql"

## 6. Sanity Check

You can run this command to go inside a pod’s container. For testing purpose let’s go inside the ui container. Some examples:
	
 	kubectl exec -it ui-deployment-5d965f954d-6xnqw -n final-project -- bash
  	apt update
	apt install curl -y
 	curl -d '{"content_filter":"germany"}' -H "Content-Type:application/json" -X POST http://ingestion-service.final-project:5001/load_records
	curl -d '{"filters":{"author":"britneyspears"}}' -H "Content-Type: application/json" -X POST http://backend-service.final-project:5002/run_query

## 7. Access The Application
In macOS environment you need to execute the following command:

	kubectl port-forward --address 0.0.0.0 svc/ui-container -n final-project 8080:5005 &

Now we can access the application interface via: http://localhost:8080/
### <ins>Home page</ins>
![image](https://github.com/mataniv/BDP_FinalProject/assets/38129502/e0d3bae1-b3eb-4306-a883-8440a32dc5d3)


### <ins>Analytics Page</ins>
![image](https://github.com/mataniv/BDP_FinalProject/assets/38129502/e4353f4d-8e02-4af9-81ea-3e67fa5ecec6)
![image](https://github.com/mataniv/BDP_FinalProject/assets/38129502/034d5059-8e75-4228-b47f-5febae2da6e5)

### <ins>Load Data Page</ins>
<img width="522" alt="image" src="https://github.com/mataniv/BDP_FinalProject/assets/38129502/c966949f-5a71-4bb9-a054-748467eb9724">

### <ins>Post Tweet Page</ins>
<img width="945" alt="image" src="https://github.com/mataniv/BDP_FinalProject/assets/38129502/a848b7ba-1552-4b38-ba42-c88c941179de">

## 8. Stop The Minikube Cluster

 	minikube stop

