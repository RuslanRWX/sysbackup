#!/usr/bin/env python

import socket
import os

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 22222

tmpfile="/tmp/backup.mysqldb.txt"
log="/var/log/sbclient"

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


#print GetData("Send:DirsInc")

def MysqlDump():
    GetData("Add:MysqlReady:NO")
    Ex=GetData("Send:DBex")
    Dir=GetData("Send:DirsInc")
    Opt=GetData("Send:MyDumpOpt")
    Ex=Ex.split(",")
    print Ex
    os.system("mysql -e \"SHOW DATABASES\" | sed '1d' > {file}".format(file=tmpfile))
    for R in Ex:
        os.system("sed -i\"\" \"/{line}/d\" {file}".format(line=R, file=tmpfile))
    file=open(tmpfile, "r")
    for line in file:
        line = line.strip('\n')
        cmd="mysqldump {opt} {line} > {dir}/{line}.sql 2>> {log}/sbclient.log ".format(opt=Opt, line=line, dir=Dir, log=log)
        os.system(cmd)
    if os.stat(log).st_size != 0:
        GetData("Add:MysqlLog:Error")
    else:
        GetData("Add:MysqlLog:Not")
    GetData("Add:MysqlReady:YES")  
        
    #print Res
    

MysqlDump()

#print GetData("DBex")
#print GetData("MyDumpOpt")




