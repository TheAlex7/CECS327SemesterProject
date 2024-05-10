# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

import sys
import time
import json
import pymongo
import socket

# search local files compiled from food network node
def searchFoodNet(query):
    result = {"name": "NONE"} # default result; if no results

    # Read the JSON file
    with open('./data/food_network_recipes.json') as json_file:
        data = json.load(json_file)

    # Search through list of dictionaries
    for obj in data:
        if query in obj["name"]:
            result = json.dumps(obj)

    return result

# search through mongoDB database; filled by scraper node(s)
def searchMongo(query):
    results = collection.find({ "name": { "$regex": query } }) # Mongo query of substring inside names
    if results.count() == 0:
        return {"name": "NONE"}
    else:
        first_result = next(results, None)
        return first_result

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((client_ip, client_port)) # Bind the socket
        
        sock.listen()

        print("Server listening on port", client_port)

        # Accept a connection
        conn, addr = sock.accept()
        with conn:
            print('Connected by', addr)

            while True:
                # Receive msg from the client
                data = conn.recv(1024).decode()

                if data[0] == "q":
                    print("Client closed. Shutting down.")
                    break  # quit message = break the loop

                method = data[0]
                query = data[2:]

                if method == '1':
                    result = searchFoodNet(query)
                else:
                    result = searchMongo(query)

                conn.sendall(result.encode())

if __name__ == "__main__":
    # connecting to mongo server
    # MUST have proper connection string
    client = pymongo.MongoClient("connection_string")
    db = client["RecipeDB"]
    collection = db["recipes"]

    # ip and port as set up in the .yml file
    client_ip = "client"
    client_port = 5002

    main()