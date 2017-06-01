#!/usr/bin/env python

import socket

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 22222


print("Connected to " + str((SERVER_ADDRESS, SERVER_PORT)))
def GetData(data):
    c = socket.socket()
    c.connect((SERVER_ADDRESS, SERVER_PORT))
    # Convert string to bytes. (No-op for python2)
    data = data.encode()

    # Send data to server
    c.send(data)

    # Receive response from server
    data = c.recv(2048)
    if not data:
        return

    # Convert back to string for python3
    data = data.decode()
    return data
    c.close()


print GetData("Dir")
print GetData("DBex")
