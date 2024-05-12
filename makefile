.DEFAULT_GOAL := build

build: # create new docker containers for the network
	@echo "Building new Docker Network..."
	@docker-compose build

fill_db:  # run scraper images on the shared volume
	@echo "Scraper node(s) filling up database..."
	@docker-compose run --volume ./data:/app/data node1

server: # run a detached server and interactive client node
	@echo "Running server in detached mode and client in iterative mode..."
	@docker-compose up -d master
	@docker-compose run -it client

server_only:
	@echo "Running server in detached mode..."
	@docker-compose up -d master

client_only:
	@echo "Running client in iterative mode."
	@docker-compose run -it client

down: # take down docker containers
	@echo "Turning off Docker Network..."
	@docker-compose down