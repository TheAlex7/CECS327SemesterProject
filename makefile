.DEFAULT_GOAL := build

build: # create new docker image along with json file containing recipes
	@echo "Building new Docker Network..."
	@docker-compose build

fill_db:  # run scraper images on the shared volume
	@echo "Scraper node(s) filling up database..."
	@docker-compose run --volume ./data:/app/data node1

server: # run a detached docker network
	@echo "Turning on Docker Network in detached mode..."
	@docker-compose up -d master
	@docker-compose run -it client

down: # take down docker network
	@echo "Turning off Docker Network..."
	@docker-compose down

inspect:
	@cat ./net-analysis/network_activities.csv