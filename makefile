.DEFAULT_GOAL := build

build: # create new docker image along with json file containing recipes
	@echo "Building new Docker Network..."
	@docker-compose build

detach: # run a detached docker network
	@echo "Turning on Docker Network in detached mode..."
	@docker-compose up -d

up:  # run current docker image
	@echo "Turning on Docker Network..."
	@docker-compose up

down: # take down docker network
	@echo "Turning off Docker Network..."
	@docker-compose down

inspect:
	@cat ./net-analysis/network_activities.csv