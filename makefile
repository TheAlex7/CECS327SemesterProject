.DEFAULT_GOAL := build

build: # create new docker image along with csv file containing network logs (analysis tool)
	@echo "Building new Docker Network..."
	@docker-compose up --build

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