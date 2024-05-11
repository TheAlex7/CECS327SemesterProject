# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

import sys
import time
import os
import json
import pymongo
import socket

# search local files compiled from food network node
def searchFoodNet(query):
    result = {"name": "NONE"} # default result; if no results

    # Read the JSON file
    with open('./data/food_network_recipes.json') as json_file:
        data = json.load(json_file)

    # Search through list of dictionaries (json objects)
    for obj in data:
        if query in obj["name"]:
            result = obj

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
        sock.bind((master_ip, master_port)) # Bind the socket
        
        sock.listen()
        print("Server listening on port", master_port)

        # Accept a connection
        conn, addr = sock.accept()
        with conn:
            print('Connected by', addr)

            while True:
                # Receive msg from the client
                data = conn.recv(1024).decode()

                if not data or data == "q":
                    print("Client disconnected. Shutting down.")
                    break  # quit message = break the loop

                method = data[0] #search method
                if len(data) <= 2 or len(data[2:].strip()) == 0: # make sure query isn't empty
                    conn.sendall(b"{\"name\":\"NONE\"}")
                    continue
                else:
                    query = data[2:].strip()

                if method == '1': # determine search method
                    result = searchFoodNet(query)
                else:
                    result = searchMongo(query)
                
                result = json.dumps(result) # convert json object into string to send through socket

                conn.sendall(result.encode())

if __name__ == "__main__":
    # time.sleep(30)

    ### connecting to mongo server
    ## MUST have proper connection string to use mongo search!!!
    client = pymongo.MongoClient("connection_string")
    db = client["RecipeDB"]
    collection = db["recipes"]
    ###

    # Use the service name as the hostname in Docker environment
    master_ip = 'master'
    # Port number on which master listens for client messages
    master_port = 6000 

    host_ip = "127.0.0.1" # The server's IP address
    host_port = 6000 # The port used by the server

    # ip and port as set up in the .yml file
    # listen_port = int(os.getenv('LISTEN_PORT'))
    client_ip = "client"
    client_port = 5002

    main()