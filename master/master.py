# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

import socket
import struct
import sys
import time
import threading
import csv

def writeLogs(data):
    # write to a csvfile. Data must already be in correct formatting
    with open('./net-analysis/network_activities.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        print("Printing to output csv")
        writer.writerow(data)

#multicast_message(message) was used from https://pymotw.com/2/socket/multicast.html
def sendMulticastMessage(message, multicast_group):
    udp_header_size = 8 # Size of UDP header
    ip_header_size = 20 # Size of IP header
    this_port = 5000 # as defined in dockerfile
    this_ip = socket.gethostbyname(socket.gethostname())

    # encode message to bytes
    storedmessage = message.encode('utf-8')

    #wait for nodes to listen to multicast port
    time.sleep(3.5)

    # Create the datagram socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    sock.settimeout(.5)

    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)    

    try:
        #calculate packet size
        pack_size = len(storedmessage) + udp_header_size + ip_header_size

        # Send data to the multicast group
        print('sending "%s"' % storedmessage)    
        sock.sendto(storedmessage, multicast_group)
        pack_data = ["Multicast", "%.7f" % (time.time() - start), this_ip, multicast_group[0], this_port, multicast_group[1], "UDP",pack_size,"N/A"]
        writeLogs(pack_data)

        # Look for responses from all recipients
        while True:
            print('waiting to receive')
            try:
                data, server = sock.recvfrom(1024) 
            except socket.timeout:
                print('timed out, no more multicast responses')
                break
            else:
                print('received "%s" from %s' % (data.decode('utf-8'), server))

    finally:
        print('closing socket')
        sock.close()

# Reference(s) : https://pymotw.com/2/socket/tcp.html
def sendUnicastMessage(node_info, cycles=1):

  udp_header_size = 8 # Size of UDP header
  ip_header_size = 20 # Size of IP header
  
  this_port = 5000 # as defined in dockerfile
  this_ip = socket.gethostbyname(socket.gethostname()) # Grabs IP for master

  # Loop through the sending process 'cycles' times
  for _ in range(cycles): 

      # Iterates over each node's info (IP & Port) in node_info list
      for node_ip, node_port in node_info:
          # Constructs message personalized to each node based on port number
          message = f"Hello from Master to node{node_port-5000}:500{node_port-5000}"
          message_bytes = message.encode()

          node_ip = socket.gethostbyname(node_ip)

          # Creates UDP socket
          with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
              # calculate packet size
              pack_size = len(message_bytes) + udp_header_size + ip_header_size

              print(f"Sending: {message}")

              sock.sendto(message_bytes, (node_ip, node_port))
              pack_data = ["Unicast", "%.7f" % (time.time() - start), this_ip, node_ip, this_port, node_port, "UDP",pack_size,"N/A"]
              writeLogs(pack_data)

              # Waits for a second before sending next message
              time.sleep(1)

      # Logs completion of cycle
      print(f"Cycle {_+1} complete.")

      # Waits 2 seconds before starting next cycle (if any)
      time.sleep(2) 

  # After all cycles are complete, send shutdown message to each node
  shutdown_message = "shutdown"
  for node_ip, node_port in node_info:
      with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
          print(f"Sending shutdown to Node {node_ip}:{node_port}")
          sock.sendto(shutdown_message.encode(), (node_ip, node_port))

# Reference(s) : https://pymotw.com/2/socket/tcp.html
def listenForAcks(ack_port=5000):

  # Create UDP socket & bind to specified port to listen
  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
      sock.bind(('', ack_port))

      # Set timeout of 5 secondds on blocking socket operations
      sock.settimeout(5)
      print(f"Master listening for acks on port {ack_port}")

      while True:
          try:
              # Wait for incoming acks; blocks until data recived or timeout occured
              data, addr = sock.recvfrom(1024) #receives a max of 1024 bytes; adjustable

              print(f"Received ack from Node {addr}: {data.decode()}")

          except socket.timeout:
              # Exit loop & shutdown master if no data received within timeout
              print("No more acks received. Master shutting down.")
              break

def main():
    #validate that csv file exists
    print("Validating network_activities.csv exists.")
    with open('./net-analysis/network_activities.csv', 'a', newline='') as csvfile:
            fieldnames = ['Type', 'Time(s)', 'Source_IP', 'Destination_IP', 'Source_Port', 
                          'Destination_Port', 'Protocol', 'Length(bytes)', 'Flags(hex)']
            writer = csv.writer(csvfile)

            # Write header if file empty
            if csvfile.tell() == 0:
                writer.writerow(fieldnames)

    # List of (IP, port) tuples for each node.
    node_info = [("node1", 5001), ("node2", 5002), ("node3", 5003), ("node4", 5004)]
    num_cycles = 1 # how many times each node in the list will be contacted

    multicast_message = "This is a multicast message."

    group = ('224.3.29.71', 10000)

    # Send multicast messages to predefined group
    sendMulticastMessage(multicast_message, group)

    time.sleep(1)

    # Send unicast messages in a separate thread
    threading.Thread(target=sendUnicastMessage, args=(node_info, num_cycles), daemon=True).start()

    # Listen for acks on the main thread
    listenForAcks()

if __name__ == "__main__":
    start = time.time()
    main()