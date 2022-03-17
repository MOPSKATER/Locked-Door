#!/bin/python3

from datetime import datetime
import socket
import sqlite3


con = sqlite3.connect('access.db')
con.execute("CREATE TABLE IF NOT EXISTS opened (time text, PRIMARY KEY (time))")
con.execute(
    "CREATE TABLE IF NOT EXISTS users (id integer, username text, salt text, password text, PRIMARY KEY (ID))")
con.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.0.185', 8888)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

sock.listen(1)

while True:
    print('Waiting for a connection')
    connection, client_address = sock.accept()
    try:
        data = connection.recv(16)
        if data == "opened":
            dt = datetime.now()
            con = sqlite3.connect('access.db')
            con.execute("INSERT INTO opened (time) VALUES (" + dt + ")")
            con.commit()
            con.close()

    finally:
        connection.close()
