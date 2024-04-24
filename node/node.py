# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

import socket
import struct
import sys
import os
import time
import csv

#recieveMulticastMessage was used from https://pymotw.com/2/socket/multicast.html
def recieveMulticastMessage(multicast_group, server_address): 
    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to the server address
    sock.bind(server_address)

    # Tell the operating system to add the socket to the multicast group
    # on all interfaces.
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print('waiting to receive multicast message')

    data, address = sock.recvfrom(1024)

    print('received %s bytes from %s' % (len(data), address))
    print(f"Message: {data.decode('utf-8')}")

    print('sending acknowledgement to', address)
    sock.sendto('ack'.encode('utf-8'), address)     

# Reference(s) : https://pymotw.com/2/socket/tcp.html
def receiveUnicastMessage():

  # Retrieve NODE_ID environment variable to identify the node
  node_id = os.getenv('NODE_ID')

  # Retrieve the LISTEN_PORT environment variable, which specifies the port this node listens for incoming messages
  listen_port = int(os.getenv('LISTEN_PORT'))

  # Use the service name as the hostname in Docker environment
  master_ip = 'master'

  # Port number on which master listens for ack messages from nodes
  master_port = 5000 

  # Create UDP socket for network communication
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

      # Bind the socket to an address & port. Emty string listens on all interfaces
      sock.bind(('', listen_port))

      # Standard print message for current node listening
      print(f"Node {node_id} listening for unicast messages on port {listen_port}")

      # Continuously listen for incoming messages
      while True:
          # Receive data from network. 
          data, addr = sock.recvfrom(1024)

          message = data.decode()

          # Indicate shutdown process
          if message == "shutdown":
            
              print(f"Node {node_id} received shutdown. Sending ack and shutting down.")
              ack_message = "shutdown ack"
              sock.sendto(ack_message.encode(), (master_ip, master_port))
              break  # Exit the loop and end the program

          # Print received message & address came from
          print(f"Node {node_id} received message: {data.decode()} from master {addr}")

          # Construct ack message indicating it's from this node
          ack_message = f"Node {node_id} ack"

          # Send ack messge back to master
          sock.sendto(ack_message.encode(), (master_ip, master_port))

          # Print message indicating the ack was sent
          print(f"Node {node_id} sent ack to master")

def main():
    # Retrieve NODE_ID environment variable to identify the node
    node_id = os.getenv('NODE_ID')
    print(f'STARTING UP NODE {node_id}')

    multicast_group = '224.3.29.71'
    server_address = ('', 10000)

    recieveMulticastMessage(multicast_group,server_address)
    time.sleep(1)
    receiveUnicastMessage()

if __name__ == "__main__":
    main()
