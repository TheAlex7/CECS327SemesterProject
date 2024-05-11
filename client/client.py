# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

# Description: TODO

import time
import socket
import os
import json

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # connect to master node (acts as server)
        sock.connect((master_ip, master_port))

        while True:
            json_file = {"name":"NONE"}
            print("Make query from...(q to quit)\n\t1) Local Json files\n\t2) MongoDB Server Client\n")
            user_decision = input()
            
            if user_decision == '1':
                query = input("Enter food to search: ")
                mquery = '1,'+query # serialized message to master node for proper query structure

            elif user_decision == '2':
                query = input("Enter food to search: ")
                mquery = '2,'+query

            elif user_decision == 'q':
                print("Quitting...")
                sock.sendall(b'q')
                break

            else:
                print("Invalid input")
                continue

            # Send query message to master
            sock.sendall(mquery.encode())

            # decode the received json response
            response = sock.recv(1024).decode()
            json_file = json.loads(response) # convert string to json obj

            if json_file["name"] == "NONE":
                print("No results.\n")
            else:
                for key, val in json_file.items():
                    if key == "id":
                        continue
                    print(f"{key}: {val}\n")

if __name__ == "__main__":
    # Retrieve NODE_ID environment variable to identify the node
    node_id = os.getenv('NODE_ID')

    # Use the service name as the hostname in Docker environment
    master_ip = 'master'
    # Port number on which master listens for ack messages from nodes
    master_port = 6000 

    time.sleep(5) # ensures server is up before client connects
    main()