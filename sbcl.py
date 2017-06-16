#!/usr/bin/env python
# Copyright (c) 2017 Ruslan Variushkin,  ruslan@host4.biz
# Version 0.3.0

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 29029

tmpfile = "/tmp/backup.mysqldb.txt"
logdir = "/var/log/sbclient"

import socket
import os
import datetime
import sys

# mail variables 
MysqlOptDef = "--opt  --routines"
PortDef = 22
UserDef = "root"
RsyncOptDef = "-av"
PrivDef = 20
DirsDef = "/etc,/var"
DirIncDef = "/var/backup"
DirExDef = "/etc/ssh,/var/log"
FrequencyDef = 24
CleanDateDef = 7
DBexDef = "information_schema,performance_schema"


# text
tStart = "##########################\n"
tServName = "Server name: "
tServIP = "Server IP: "
tUser = "User:"
tServPort = "Server ssh port: "
tPriy = "Priority: "
tOpR = "Options of rsync: "
tLastD = "Last backup start time: "
tLastDN = "Last backup finish time: "
tDirB = "Directories of backup "
tDirBx = "Directories of exclude "
tFB = "Frequency of backup, hours: "
tCleanB = "Clean the backup server, days: "
tAOS = "##########################"
tHavenot = "Haven't got any host !\nBye "
tCheckInf = "Check information\nName: "
tDir = "Directory :"
tDirEx = "Exclude directory :"
tDataCor = "Data are correct? yes|no: "
tBye = "Bye!"
tPlease = "Please respond with 'yes' or 'no'"
tAddsshKey = "Add sshkey, please, prepare to enter a password of remote server of its first to connect"
tDuD = 'Do you really want to delete host? '
tDirBInc = "Mysqldump directory: "
tDoUBackupMysql = "Do you want to backup MySQL? yes|no: "
tResdf = "Result of \"df -h\" on your remote server"
tInstClient = "Install a cleant for MySQL backuing "
tDoUexdb = "Do you want to exclude any databases? yes|no: "
tUdb = "Your databases: "
tDBex = "Exclude databases: "
tChmy = "Backup mysql: "
tMyDumpOpt = "MySQL dump options: "
tMysqlLog = "MysqlLog: "
tSbcltext = "Add a job in /etc/crontab, default: [ "
tSbclCron = "0 0    * * * root /usr/sbin/sbcl.py mysqldump"
tSbcltext2 = " ] You can add other job, format for crontab file : "
tDateStartMysql = "Mysqldump start localtime: "
tDateStopMysql = "Mysqldump stop localtime: "
tMysqlUpdate = "Do you want to configuration mysqldump on the remote host ? ['yes','no' or 'rm' (for remove) ]: "
tNote = """Note that rsync must be installed on your remote server.
If you using mysql backup, please, check that mysqldump is installed and a local configuration file ~/.my.cnf is configured """
tCheckRsync = "Is the Rsync installed on your remote server ? ['yes' or 'no']: "
tPlInR = "Please, install the rsync on your remote server !"
tCheckMy = "Is the file ~/.my.cnf configured ?  ['yes' or 'no']: "
tPlconfMy = "Please, configure the ~/.my.cnf for databases access "
tDefMysqlOpt = " you can add --ignore-table=db.table [default: " + MysqlOptDef + " ]: "
tdefExDb =  "[default: information_schema,performance_schema]: "
tDuDel = "Do you want to purge ['yes' or 'on']: "
Defroot = "[default:"+UserDef+"] "
Defport = "[default: "+ str(PortDef) +" ] "
Defop = "[default:"+RsyncOptDef+"] "
Defpri = "[default: "+  str(PrivDef) +" ] "
DefFr = "[default: "+ str(FrequencyDef) +"] "
DefClean = "[default "+ str(CleanDateDef)+"] "
ExampleDir = "example["+DirsDef+"] "
ExampleDirEx = "example["+DirExDef+"] "
ExampleIncDir = "example["+DirIncDef+"] " 
ExampleExDB = "example["+DBexDef+"] "
tStatus = "Status: "
tDelCronResult = "Cron job sbcl.py has been removed on the remote host"
tAddtoCron = " add to /etc/crontab"
tEndofUpdate = "Configuration has been modified"

#print("Connected to " + str((SERVER_ADDRESS, SERVER_PORT)))
if not os.path.exists(logdir):
    os.makedirs(logdir)
with open(logdir+"/sbclient.error.log", 'w'): pass


def ImCheck(data, default=None, Empty=None):
    Check = None
    while Check is None:
        Result=raw_input(data).replace(' ', '').replace('\t', '') or default
        if Result != "" and Result is not None or Empty == "YES" :
            Check="True"
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
    if Dir == "Empty":
        print "Not configured on the backup server for mysqldump"
        return
    print "Start backup"
    cmd="mysql -e \"SHOW DATABASES\" | sed '1d' > {file}".format(file=tmpfile)
    os.system(cmd)
    if Ex != "Empty":
        for R in Ex:
            cmd="sed -i\"\" \"/{line}/d\" {file}".format(line=R, file=tmpfile)
            os.system(cmd)
    file = open(tmpfile, "r")
    for line in file:
        line = line.strip('\n')
        cmd = "mysqldump {opt} {line} > {dir}/{line}.sql 2>> {logdir}/sbclient.error.log ".format(
            opt=Opt, line=line, dir=Dir, logdir=logdir)
        os.system(cmd)
    if os.stat(logdir+"/sbclient.error.log").st_size > 0:
        GetData("Add|MysqlLog|Error")
    else:
        GetData("Add|MysqlLog|Not")
    GetData("Add|MysqlReady|YES")
    ISODateStop = datetime.datetime.now().isoformat()
    GetData("Add|DateStopMySQL|"+ISODateStop)
    print "Mysqldump has been done"


def list():
        global ServerName
        ServerName = GetData("Get|Name")
        global User
        User = GetData("Get|User")
        global ServerPort
        ServerPort = GetData("Get|ServerPort")
        global Priv
        Priv = GetData("Get|Priv")
        global RsyncOpt
        RsyncOpt = GetData("Get|RsyncOpt")
        global Dirs
        Dirs = GetData("Get|Dirs")
        global DirsExclude
        DirsExclude = GetData("Get|DirsExclude")
        global Frequency
        Frequency = GetData("Get|Frequency")
        global CleanDate
        CleanDate = GetData("Get|CleanDate")
        global Chmy
        Chmy = GetData("Get|Chmy")
        global DBex
        DBex = GetData("Get|DBex")
        global MyDumpOpt
        MyDumpOpt = GetData("Get|MyDumpOpt")
        global DirsInc
        DirsInc = str(GetData("Get|DirsInc"))
        global MysqlLog
        MysqlLog = GetData("Get|MysqlLog")
        print tStart
        print tServName,  ServerName
        print tUser,  User
        print tServPort,  ServerPort
        print tPriy,  Priv
        print tOpR + RsyncOpt
        print tStatus  + GetData("Get|Status")
        print tLastD + GetData("Get|DateStart")
        print tLastDN + GetData("Get|DateEnd")
        print tDir + Dirs
        print tDirEx + DirsExclude
        print tFB,  Frequency
        print tCleanB, CleanDate
        print tChmy, Chmy
        if Chmy == 'YES':
            print tDirBInc + DirsInc
            print tDBex + DBex
            print tMyDumpOpt + MyDumpOpt
            if MysqlLog == "Error":
                print tMysqlLog + MysqlLog 
            print tDateStartMysql + GetData("Get|DateStartMySQL")
            print tDateStopMysql + GetData("Get|DateStopMySQL")+"\n"
        print tAOS

def list2():
    data = GetData("GetAll|None")
    print data
    
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
        tOpR + Defop + ' [Now:' + RsyncOpt + ']: ', default=RsyncOpt)
    PrivN = ImCheck(tPriy  + ' [ Now:' + str(Priv) + ' ]: ', default=Priv)
    DirsN = ImCheck(tDir + ExampleDir +' [ Now:' + Dirs + ' ]: ', default=Dirs)
    DirsExcludeN = ImCheck(
        tDirEx + ExampleDirEx + ' [ Now:' + DirsExclude + ']: ', default=DirsExclude, Empty="YES")
    FrequencyN = ImCheck(
        tFB + ' [ Now:' + Frequency + ' ]: ', default=Frequency)
    yes = set(['yes', 'y', 'ye'])
    no = set(['no', 'n'])
    rm = set(['rm'])
    choice = ImCheck(tMysqlUpdate).lower()
    cmdcrondel = "sed -i '/sbcl.py/d' /etc/crontab"
    if choice in "rm":
        ChmyN="NO"
    elif choice in yes:
        ChmyN="YES"
        choicech = ImCheck(tCheckMy).lower()
        if choicech in yes:
            pass
        else:
            print tPlconfMy
            return
        cmddb="mysql -e 'show databases;'"
        cmddf="df -h"
        print tResdf
        os.system(cmddf)
        if DirsInc == "Empty":
            DirsIncExample = DirIncDef
        else:
            DirsIncExample = DirsInc
        DirsIncN = ImCheck(
            tDirBInc + ExampleIncDir  + ' [ Now:' + DirsInc + ' ]: ', default=DirsIncExample)
        print tUdb
        os.system(cmddb)
        print tAOS
        if DBex == "Empty":
            DBexExample = DBexDef
        else:
            DBexExample = DBex
        DBexN = ImCheck(tDBex + ExampleExDB + '[Now: '+DBex+']: ', DBexExample,  Empty="YES")
        if MyDumpOpt == "Empty":
            MyDumpOptExample = MysqlOptDef
        else:
            MyDumpOptExample = MyDumpOpt
        MyDumpOptN = ImCheck(tMyDumpOpt + tDefMysqlOpt + '[Now:'+MyDumpOpt+']:', default=MyDumpOptExample)
        CronN = ImCheck(tSbcltext + tSbclCron + tSbcltext2, default=tSbclCron)
        print CronN + tAddtoCron
        cmdcron = "echo \"" + CronN + "\" >> /etc/crontab"    
    else:
        pass
    if  ChmyN == "NO":
        MyDumpOptN="Empty"
        DirsIncN="Empty"
        DBexN="Empty"
    choice = ImCheck(tDataCor).lower()
    if choice in yes:
        if ServerName != ServerNameN:
            GetData("Add|Name|"+ServerNameN)
        if User != UserN:
            GetData("Add|User|"+UserN)
        if ServerPort != ServerPortN:
            GetData("Add|ServerPort|"+ServerPortN)
        if RsyncOpt != RsyncOptN:
            GetData("Add|RsyncOpt|"+RsyncOptN)
        if Dirs != DirsN:
            GetData("Add|Dirs|"+DirsN)
        if DirsExclude != DirsExcludeN:
            GetData("Add|DirsExclude|"+DirsExcludeN)
        if Priv !=PrivN:
            GetData("Add|Priv|"+PrivN)
        if Frequency != FrequencyN:
            GetData("Add|Frequency|"+FrequencyN)
        if ChmyN is not None and Chmy != ChmyN:
            GetData("Add|Chmy|"+ChmyN)
        if  ChmyN == "YES":
            if DirsInc != DirsIncN:
                GetData("Add|DirsInc|"+DirsIncN)
            if DBex != DBexN:
                GetData("Add|DBex|"+DBexN)
            if MyDumpOpt != MyDumpOptN:
                GetData("Add|MyDumpOpt|"+MyDumpOptN)
            os.system(cmdcrondel)
            os.system(cmdcron)
        elif ChmyN == "NO" and Chmy == "YES":
            os.system(cmdcrondel)
        else: 
            pass
        print tEndofUpdate
    elif choice in no:
        print tBye
        return exit(1)
    else:
        sys.stdout.write(tPlease)

def help():
    return """Help function: Basic Usage:
    \tmysqldump     - Start mysqldump
    \tlist          - list,show your configurations 
    \tbackup        - Add status needbackup, it mean the backup server will start a backup script as fast as it can
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
    
