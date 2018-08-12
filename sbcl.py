#!/usr/bin/env python
# cbcl - SySBackup client program
# Copyright (c) 2017 Ruslan Variushkin,  ruslan@host4.biz
Version = "0.4.4"

import socket
import os
import datetime
import sys
import signal
import readline
import bson
import pickle
import ConfigParser
import variablessbcl
from variablessbcl import *

def signal_handler(signal, frame):
            print tctrlD
            sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print Pathini

config = ConfigParser.ConfigParser()
config.read(Pathini)


SERVER_ADDRESS = config.get("Main", "IP")
SERVER_PORT = int(config.get("Main", "PORT"))
tmpfile = config.get("Main", "tmpfile")
logdir = config.get("Main", "logdir")


if not os.path.exists(logdir):
    os.makedirs(logdir)


def Text_Style(data, color="YELLOW"):
    from colorama import Fore, Style
    Color = getattr(Fore, color)
    return (Color + data + Style.RESET_ALL)


#print("Connected to " + str((SERVER_ADDRESS, SERVER_PORT)))
with open(logdir + "/sbclient.error.log", 'w'):
    pass


def ImCheck(data, default=None, Empty=None, Space=None):
    Check = None
    if Space is not None:
        Result = raw_input(data) or default
        return Result
    while Check is None:
        Result = raw_input(data).replace(' ', '').replace('\t', '') or default
        if Result != "" and Result is not None or Empty == "YES":
            Check = "True"
    return Result


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
    data = data.decode()
    c.close()
    return data
    
    
def Pikle():
    data = GetData("GetAll|None")
    return pickle.loads(data)


def list():
    R=Pikle()
    global ServerName
    ServerName = R[0]["Name"]
    global User
    User = R[0]["User"]
    global ServerIP
    ServerIP = R[0]["ServerIP"]
    global ServerPort
    ServerPort = R[0]["ServerPort"]
    global Priv
    Priv = R[0]["Priv"]
    global RsyncOpt
    RsyncOpt = R[0]["RsyncOpt"]
    global Dirs
    Dirs = R[0]["Dirs"]
    global DirsExclude
    DirsExclude = R[0]["DirsExclude"]
    global Frequency
    Frequency = R[0]["Frequency"]
    global Status
    Status = R[0]["Status"]
    global Chmy
    Chmy = R[0]["Chmy"]
    global DBex
    DBex = R[0]["DBex"]
    global MyDumpOpt
    MyDumpOpt = R[0]["MyDumpOpt"]
    global DirsInc
    DirsInc = str(R[0]["DirsInc"])
    global MysqlLog
    MysqlLog = R[0]["MysqlLog"]
    global MysqlReady
    MysqlReady = R[0]["MysqlReady"]
    global Desc
    Desc = R[0]["Desc"]
    global NodeName
    NodeName = R[0]["NodeName"]
    
    print tStart
    print Text_Style(tServName + ServerName, color="WHITE")
    print Text_Style(tUser +" "+ User, color="WHITE")
    print tPriy, Priv
    print tOpR + RsyncOpt
    if Status == "rsync error":
        print Text_Style(tStatus + Status, color="RED")
    elif Status == "running":
        print tStatus + Status
    else:
        print tStatus + Status
    if R[0]["DateStart"]:
        print tLastD + R[0]["DateStart"]
    if R[0]["DateEnd"]:
        print Text_Style(tLastDN + R[0]["DateEnd"])
    print tDir + Dirs
    print tDirEx + DirsExclude
    print tFB + str(Frequency)
    print tChmy, Chmy
    if Chmy == 'YES':
        print tDirBInc + DirsInc
        print tDBex + DBex
        print tMyDumpOpt + MyDumpOpt
        if MysqlLog == "Error":
            print Text_Style(tMysqlLog + MysqlLog, color="RED")
        if MysqlReady == "YES":
            print tMysqlReady + MysqlReady
        else:
            print tMysqlReady + MysqlReady
        print tDateStartMysql + R[0]["DateStartMySQL"]
        print tDateStopMysql + R[0]["DateStopMySQL"] + "\n"
    if Desc != "":
        print Text_Style(tDesc + Desc)
    print Text_Style(tNodeName + NodeName)
    print tAOS


def MysqlDump():
    R=Pikle()
    Ex = R[0]["DBex"]
    Dir = R[0]["DirsInc"]
    try:
        os.stat(Dir)
    except:
        os.mkdir(Dir)
    Opt = R[0]["MyDumpOpt"]
    ISODateStart = datetime.datetime.now().isoformat()
    GetData("Add|DateStartMySQL|" + ISODateStart)
    GetData("Add|DateStopMySQL|None")
    if Dir == "Empty":
        print "Not configured on the backup server for mysqldump"
        return
    print "Start backup"
    cmd = "mysql -e \"SHOW DATABASES\" | sed '1d' > {file}".format(
        file=tmpfile)
    os.system(cmd)
    if Ex != "Empty":
        for R in Ex.split(","):
            cmd = "sed -i \"/{line}/d\" {file}".format(line=R, file=tmpfile)
            os.system(cmd)
    file = open(tmpfile, "r")
    for line in file:
        line = line.strip('\n')
        cmd = "mysqldump {opt} {line} > {dir}/{line}.sql 2>> {logdir}/sbclient.error.log ".format(
            opt=Opt, line=line, dir=Dir, logdir=logdir)
        os.system(cmd)
    if os.stat(logdir + "/sbclient.error.log").st_size > 0:
        GetData("Add|MysqlLog|Error")
    else:
        GetData("Add|MysqlLog|Not")
    GetData("Add|MysqlReady|YES")
    ISODateStop = datetime.datetime.now().isoformat()
    GetData("Add|DateStopMySQL|" + ISODateStop)
    print "Mysqldump has been done"


def update():
    list()
    ChmyN = None
    ServerNameN = ImCheck(
        tServName + ' [Now:' + ServerName + ']: ', default=ServerName)
    UserN = ImCheck(
        tUser + Defroot + ' [Now:' + User + ']: ', default=User)
    ServerPortN = ImCheck(
        tServPort + Defport + ' [Now: ' + str(ServerPort) + ' ] : ', default=ServerPort)
    RsyncOptN = ImCheck(
        tOpR + Defop + ' [Now:' + RsyncOpt + ']: ', default=RsyncOpt, Space="True")
    PrivN = ImCheck(tPriy + ' [ Now:' + str(Priv) + ' ]: ', default=Priv)
    DirsN = ImCheck(tDir + ExampleDir +
                    ' [ Now:' + Dirs + ' ]: ', default=Dirs)
    DirsExcludeN = ImCheck(
        tDirEx + ExampleDirEx + ' [ Now:' + DirsExclude + ']: ', default=DirsExclude, Empty="YES")
    FrequencyN = ImCheck(
        tFB + ' [ Now:' + Frequency + ' ]: ', default=Frequency)
    yes = set(['yes', 'y', 'ye'])
    no = set(['no', 'n'])
    rm = set(['rm'])
    choice = ImCheck(tMysqlUpdate).lower()
    cmdcrondel = "sed -i '/sbcl/d' /etc/crontab"
    if choice in "rm":
        ChmyN = "NO"
    elif choice in yes:
        ChmyN = "YES"
        choicech = ImCheck(tCheckMy).lower()
        if choicech in yes:
            pass
        else:
            print tPlconfMy
            return
        cmddb = "mysql -e 'show databases;'"
        cmddf = "df -h"
        print tResdf
        os.system(cmddf)
        if DirsInc == "Empty":
            DirsIncExample = DirIncDef
        else:
            DirsIncExample = DirsInc
        DirsIncN = ImCheck(
            tDirBInc + ExampleIncDir + ' [ Now:' + DirsInc + ' ]: ', default=DirsIncExample)
        print tUdb
        os.system(cmddb)
        print tAOS
        if DBex == "Empty":
            DBexExample = DBexDef
        else:
            DBexExample = DBex
        DBexN = ImCheck(tDBex + ExampleExDB +
                        '[Now: ' + DBex + ']: ', DBexExample,  Empty="YES")
        if MyDumpOpt == "Empty":
            MyDumpOptExample = MysqlOptDef
        else:
            MyDumpOptExample = MyDumpOpt
        MyDumpOptN = ImCheck( 
            tMyDumpOpt + tDefMysqlOpt + '[Now:' + MyDumpOpt + ']:', default=MyDumpOptExample, Space="True")
        CronN = ImCheck(tSbcltext + tSbclCron + tSbcltext2, default=tSbclCron, Space="True")
        print CronN + tAddtoCron
        cmdcron = "echo \"" + CronN + "\" >> /etc/crontab"
    else:
        pass
    if ChmyN == "NO":
        MyDumpOptN = "Empty"
        DirsIncN = "Empty"
        DBexN = "Empty"
    DescN = ImCheck(
        tDescrm,  default=Desc, Space="True" )
    if DescN == "rm": DescN = ""
    choice = ImCheck(tDataCor).lower()
    if choice in yes:
        if ServerName != ServerNameN:
            GetData("Add|Name|" + ServerNameN)
        if User != UserN:
            GetData("Add|User|" + UserN)
        if ServerPort != ServerPortN:
            GetData("Add|ServerPort|" + ServerPortN)
        if RsyncOpt != RsyncOptN:
            GetData("Add|RsyncOpt|" + RsyncOptN)
        if Dirs != DirsN:
            GetData("Add|Dirs|" + DirsN)
        if DirsExclude != DirsExcludeN:
            GetData("Add|DirsExclude|" + DirsExcludeN)
        if Priv != PrivN:
            GetData("Add|Priv|" + PrivN)
        if Frequency != FrequencyN:
            GetData("Add|Frequency|" + FrequencyN)
        if ChmyN is not None and Chmy != ChmyN:
            GetData("Add|Chmy|" + ChmyN)
        if Desc != DescN:
            GetData("Add|Desc|" + DescN)
        if ChmyN == "YES":
            if DirsInc != DirsIncN:
                GetData("Add|DirsInc|" + DirsIncN)
            if DBex != DBexN:
                GetData("Add|DBex|" + DBexN)
            if MyDumpOpt != MyDumpOptN:
                GetData("Add|MyDumpOpt|" + MyDumpOptN)
            os.system(cmdcrondel)
            os.system(cmdcron)
        elif ChmyN == "NO" and Chmy == "YES":
            os.system(cmdcrondel)
        else:
            pass
        print tEndofUpdate
    elif choice in no:
        print tBye
        return sys.exit(1)
    else:
        sys.stdout.write(tPlease)


def help():
    return """Version """+Version+"""
    \nHelp function: Basic Usage:
    \tmysqldump     - Start mysqldump
    \tlist          - list,show your configurations 
    \tbackup        - Add status needbackup, it mean the backup server will start a backup script as soon as possible
    \treconf        - Reconfiguration of backup settings 
    """


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'mysqldump':
            MysqlDump()
        elif sys.argv[1] == 'list':
            list()
        elif sys.argv[1] == 'backup':

            print "Send command to backup"
            GetData("Add|Status|needbackup")
        elif sys.argv[1] == 'reconf':
            update()
        else:
            print help()
    except IndexError:
        print help()
    except EOFError:
        print tBye

