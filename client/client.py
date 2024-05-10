import socket
import os
import time
import json

# sends query message to master.
#  method parameter decides where to search from
#    method = 1; search through local json files
#    method = 2; make search through mongoDB 
def queryToMaster(method,query=''):
    mquery = str(method)+','+query # serialized message to master node for proper query structure
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # connect to master node (acts as server)
        sock.connect((master_ip, master_port))
        # Send query message to master
        sock.sendall(mquery.encode(), (master_ip, master_port))

        # decode the received json response
        response = sock.recv(1024).decode()
        json_file = json.loads(response) #format it correctly

        return json_file

def main():
    while True:
        res = {"name":"NONE"}
        print("Make query from...(q to quit)\n\t1) Local Json files\n\t2) MongoDB Server Client\n")
        user_decision = input()

        if user_decision == '1':
            query = input("Enter food to search: ")
            res = queryToMaster(1,query)

        elif user_decision == '2':
            query = input("Enter food to search: ")
            res = queryToMaster(2,query)

        elif user_decision == 'q':
            print("Quitting...")
            queryToMaster('q')
            break

        else:
            print("Invalid input")
            continue

        if res["name"] == "NONE":
            print("No results.\n")
        else:
            for key, val in res.items():
                print(f"{key}: {val}")

if __name__ == "__main__":
    time.sleep(10)
    # Retrieve NODE_ID environment variable to identify the node
    node_id = os.getenv('NODE_ID')

    # Retrieve the LISTEN_PORT environment variable, which specifies the port this node listens for incoming messages
    # listen_port = int(os.getenv('LISTEN_PORT'))

    # Use the service name as the hostname in Docker environment
    master_ip = 'master'

    # Port number on which master listens for ack messages from nodes
    master_port = 5000 
    time.sleep(5) #ensure server is up before client tries to connect
    main()