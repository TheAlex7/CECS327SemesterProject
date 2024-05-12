How to run docker network/nodes:

First run this command to build the images for the docker nodes:
make

Then allow the scraper node to populate the local database with the following command (may take some time): 
make fill_db

Once database is done compiling, start the server and client connection with this command:
make server

NOTE: to enable mongoDB functionalities you must enter your own connection string into
        master/master.py (line 70)
        food_network_scraper/food_network.py (line 176)
    And you must also uncomment line 111 inside food_network_scraper/food_network.py
    to enable writing to the mongo database

you may take down docker networks and containers with:
make down