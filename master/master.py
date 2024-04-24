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

def main():
    with open('./data/network_activities.csv', 'a', newline='') as csvfile:
            fieldnames = ['Type', 'Time(s)', 'Source_IP', 'Destination_IP', 'Source_Port', 
                          'Destination_Port', 'Protocol', 'Length(bytes)', 'Flags(hex)']
            writer = csv.writer(csvfile)

            # Write header if file empty
            if csvfile.tell() == 0:
                writer.writerow(fieldnames)

if __name__ == "__main__":
    start = time.time()
    main()