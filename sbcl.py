#!/usr/bin/env python

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 29029

tmpfile = "/tmp/backup.mysqldb.txt"
logdir = "/var/log/sbclient"

import socket
import os
import datetime

print("Connected to " + str((SERVER_ADDRESS, SERVER_PORT)))
if not os.path.exists(logdir):
    os.makedirs(logdir)
with open(logdir+"/sbclient.error.log", 'w'): pass

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


def MysqlDump():
    GetData("Add|MysqlReady|NO")
    Ex = GetData("Get|DBex")
    Dir = GetData("Get|DirsInc")
    Opt = GetData("Get|MyDumpOpt")
    Ex = Ex.split(",")
    ISODateStart = datetime.datetime.now().isoformat()
    GetData("Add|DateStartMySQL|"+ISODateStart)
    GetData("Add|DateStopMySQL|None")
    print "Start backup"
    cmd="mysql -e \"SHOW DATABASES\" | sed '1d' > {file}".format(file=tmpfile)
    os.system(cmd)
    if Ex != "None":
        for R in Ex:
            cmd="sed -i\"\" \"/{line}/d\" {file}".format(line=R, file=tmpfile)
            os.system(cmd)
    file = open(tmpfile, "r")
    for line in file:
        line = line.strip('\n')
        cmd = "mysqldump {opt} {line} > {dir}/{line}.sql 2>> {logdir}/sbclient.error.log ".format(
            opt=Opt, line=line, dir=Dir, logdir=logdir)
        os.system(cmd)
    if os.stat(logdir).st_size != 0:
        GetData("Add|MysqlLog|Error")
    else:
        GetData("Add|MysqlLog|Not")
    GetData("Add|MysqlReady|YES")
    ISODateStop = datetime.datetime.now().isoformat()
    GetData("Add|DateStopMySQL|"+ISODateStop)
    print "Mysqldump has been done"


if __name__ == '__main__':
    MysqlDump()
    
    
