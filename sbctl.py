#!/usr/bin/python
# sbctl - SySBackup management program
# Copyright (c) 2017 Ruslan Variushkin,  ruslan@host4.biz
Version = "0.4.1"

import sys
import os
import re
import signal
import readline
sys.path.append("lib/")
import SB


# mail variables
MysqlOptDef = "--opt  --routines"
PortDef = "22"
UserDef = "root"
RsyncOptDef = "-av"
PrivDef = "20"
DirsDef = "/etc,/var"
DirIncDef = "/var/backup"
DirExDef = "/etc/ssh,/var/log"
FrequencyDef = "24"
CleanDateDef = "7"
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
tAOS = "##########################    amount of servers "
tHavenot = "Haven't got any host !\nBye "
tCheckInf = "Check information\nName: "
tDir = "Directory :"
tDirEx = "Exclude directory :"
tDataCor = "Are these data correct ? yes|no: "
tBye = "Bye!"
tctrlD = "\nYou pressed Ctrl+C!\nBye!"
tPlease = "Please respond with 'yes' or 'no'"
tAddsshKey = "Add sshkey, please, prepare to enter a password of remote server of its first to connect"
tDuD = "Do you really want to delete host 'yes' or 'no'? "
tDirBInc = "Mysqlump directory: "
tDoUBackupMysql = "Do you want to backup MySQL? yes|no: "
tResdf = "Result of \"df -h\" on your remote server"
tInstClient = "A client for MySQL backuping has been installed to the remote host, sbcl"
tDoUexdb = "Do you want to exclude any databases? yes|no: "
tUdb = "Your databases: "
tDBex = "Exclude databases: "
tChmy = "Backup mysql: "
tMyDumpOpt = "MySQL dump options: "
tMysqlLog = "MysqlLog: "
tSbcltext = "Add a job in /etc/crontab, default: [ "
tSbclCron = "0 0    * * * root /usr/sbin/sbcl mysqldump"
tSbcltext2 = " ] You can add other job, format for crontab file : "
tDateStartMysql = "Mysqldump start localtime: "
tDateStopMysql = "Mysqldump stop localtime: "
tMysqlUpdate = "Do you want to reconfiguration mysqldump on the remote host ? ['yes','no' or 'rm' (for remove) ]: "
tNote = """Note that rsync must be installed on your remote server.
If you using mysql backup, please, check that mysqldump is installed and a local configuration file ~/.my.cnf is configured """
tCheckRsync = "Is the Rsync installed on your remote server ? ['yes' or 'no']: "
tPlInR = "Please, install the rsync on your remote server !"
tCheckMy = "Is the file ~/.my.cnf configured ?  ['yes' or 'no']: "
tPlconfMy = "Please, configure the ~/.my.cnf for databases access "
tDefMysqlOpt = " you can add --ignore-table=db.table [default: " + \
    MysqlOptDef + " ]: "
tdefExDb = "[default: information_schema,performance_schema]: "
tDuDel = "Do you want to purge ['yes' or 'on']: "
Defroot = "[default:" + UserDef + "] "
Defport = "[default: " + str(PortDef) + " ] "
Defop = "[default:" + RsyncOptDef + "] "
Defpri = "[default: " + str(PrivDef) + " ] "
DefFr = "[default: " + str(FrequencyDef) + "] "
DefClean = "[default " + str(CleanDateDef) + "] "
ExampleDir = "example[" + DirsDef + "] "
ExampleDirEx = "example[" + DirExDef + "] "
ExampleIncDir = "example[" + DirIncDef + "] "
ExampleExDB = "example[" + DBexDef + "] "
tStatus = "Status: "
tDelCronResult = "Cron job sbcl has been removed on the remote host"
tAddtoCron = " add to /etc/crontab"
tEndofUpdate = "Configuration has been modified"
tMysqlReady = "MySQLdump ready: "
tMysqlLog = "MysqlLog :"
tUsestat = "\n\nPlease, use Done/Disabled/needbackup. Examlpe: sbctl statup w1.host.com Done"
tStatdone = "\n\nStatus has been updated"
tUpdateCl = "Start update sbcl : "
tDesc = "Description :"
tDescrm = "Description [rm - for remove description]: "


def Text_Style(data, color="YELLOW"):
    from colorama import Fore, Style
    Color = getattr(Fore, color)
    return (Color + data + Style.RESET_ALL)


def signal_handler(signal, frame):
            print Text_Style(tctrlD)
            sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def MongoIn(Name, User, ServerIP, ServerPort, RsyncOpt,
            Priv, Dirs, DirsExclude, Frequency, CleanDate, Chmy, MyDumpOpt, DirsInc, DBex, Desc):
    SB.MongoCon()
    data = [{"Name": Name, "User": User,  "ServerIP": ServerIP, "ServerPort": ServerPort,
             "RsyncOpt": RsyncOpt, "Priv": Priv, "Dirs": Dirs, "DirsExclude": DirsExclude, "DateStart": "",
             "DateEnd": "", "Frequency": Frequency,  "CleanDate": CleanDate, "Chmy": Chmy, "MyDumpOpt": MyDumpOpt,
             "DirsInc": DirsInc, "DBex": DBex,  "MysqlReady": "Empty", "MysqlLog": "", "DateStartMySQL": "",
             "DateStopMySQL": "", "Status": "Never", "Desc": Desc }]
    SB.coll.insert(data, True)


def List(allservers):
    global count
    count = 0
    for R in allservers:
        count = count + 1
        global ServerName
        ServerName = R['Name']
        global User
        User = R['User']
        global ServerIP
        ServerIP = R['ServerIP']
        global ServerPort
        ServerPort = R['ServerPort']
        global Priv
        Priv = R['Priv']
        global RsyncOpt
        RsyncOpt = R['RsyncOpt']
        global Dirs
        Dirs = R['Dirs']
        global DirsExclude
        DirsExclude = R['DirsExclude']
        global Frequency
        Frequency = R['Frequency']
        global CleanDate
        CleanDate = R['CleanDate']
        global id
        id = R['_id']
        global Status
        Status = R['Status']
        global Chmy
        Chmy = R['Chmy']
        global DBex
        DBex = R['DBex']
        global MyDumpOpt
        MyDumpOpt = R["MyDumpOpt"]
        global DirsInc
        DirsInc = str(R["DirsInc"])
        global MysqlLog
        MysqlLog = R["MysqlLog"]
        global MysqlReady
        MysqlReady = R["MysqlReady"]
        global Desc
        Desc = R["Desc"]

        print tStart
        print Text_Style(tServName + ServerName)
        print Text_Style(str(tServIP + ServerIP + "\n"))
        print tUser, User
        print tServPort, ServerPort
        print tPriy, Priv
        print tOpR + RsyncOpt
        if Status == "rsync error":
            print Text_Style(tStatus + Status, color="RED")
        elif Status == "running":
            print Text_Style(tStatus + Status)
        else:
            print tStatus + Status
        if R['DateStart']:
            print tLastD + R['DateStart']
        if R['DateEnd']:
            print Text_Style(tLastDN + R['DateEnd'])
        print tDir + Dirs
        print tDirEx + DirsExclude
        print Text_Style(tFB + str(Frequency))
        print tCleanB, CleanDate
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
                print Text_Style(tMysqlReady + MysqlReady, color="RED")
            print tDateStartMysql + R['DateStartMySQL']
            print tDateStopMysql + R['DateStopMySQL'] + "\n"
        if Desc != "":
            print Text_Style(tDesc+Desc)
    print tAOS, count
    if count == 0:
        print tHavenot
        sys.exit(0)


def MongoList(pattern={}):
    SB.MongoCon()
    allservers = list(SB.coll.find(pattern))
    return List(allservers)


def PrCheck(Name, User, ServerIP, ServerPort, RsyncOpt, Priv, Dirs, DirsExclude, Frequency, CleanDate):
    print tCheckInf + Name + "\n" + tUser, User, "\n" + tServIP, ServerIP, "\n" + tServPort,  ServerPort
    print tOpR + RsyncOpt + "\n" + tPriy,  Priv, "\n" + tDir + Dirs + "\n" + tDirEx + DirsExclude
    print tFB, Frequency, "\n" + tCleanB, CleanDate


def ImCheck(data, default=None, Empty=None,  Space=None):
    Check = None
    if Space is not None:
        Result = raw_input(data) or default
        return Result
    while Check is None:
        Result = raw_input(data).replace(' ', '').replace('\t', '') or default
        if Result != "" and Result is not None or Empty == "YES":
            Check = "True"
    return Result


def ImCheckIP(data, default=""):
    checkip = "True"
    while checkip:
        Result = raw_input(data) or default
        pat = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        resultip = pat.match(Result)
        if resultip:
            checkip = None
    return Result


def MongoUpdate(Name):
    CronN = None
    ChmyNReal = None
    MongoList(pattern={"Name": Name})
    MyDumpOptN = MyDumpOpt
    DirsIncN = DirsInc
    DBexN = DBex
    ChmyN = Chmy
    MysqlReadyN = MysqlReady
    if count == 0:
        return
    if Chmy == "NO":
        tRmDel = None
    ServerNameN = ImCheck(
        tServName + ' [Now:' + ServerName + ']: ',  default=ServerName)
    ServerIPN = ImCheckIP(
        tServIP + ' [Now:' + ServerIP + ']: ', default=ServerIP)
    UserN = ImCheck(
        tUser + Defroot + ' [Now:' + User + ']: ',  default=User)
    ServerPortN = ImCheck(
        tServPort + Defport + ' [Now: ' + ServerPort + ' ]: ', default=ServerPort)
    RsyncOptN = ImCheck(
        tOpR + Defop + ' [Now:' + RsyncOpt + ']: ', default=RsyncOpt, Space = "True")
    PrivN = ImCheck(
        tPriy + ' [ Now:' + str(Priv) + ' ]: ', default=Priv)
    DirsN = ImCheck(tDir + ExampleDir +
                    ' [ Now:' + Dirs + ' ]: ', default=Dirs)
    DirsExcludeN = ImCheck(
        tDirEx + ExampleDirEx + ' [ Now:' + DirsExclude + ']: ', default=DirsExclude,  Empty="YES")
    FrequencyN = ImCheck(
        tFB + ' [ Now:' + str(Frequency) + ' ]: ', default=Frequency)
    CleanDateN = ImCheck(
        tCleanB + ' [ Now:' + str(CleanDate) + ' ]: ', default=CleanDate)
    # PrCheck(ServerNameN, UserN, ServerIPN, ServerPortN, RsyncOptN,
    #        PrivN, DirsN, DirsExcludeN, FrequencyN, CleanDateN)
    yes = set(['yes', 'y', 'ye'])
    no = set(['no', 'n'])
    rm = set(['rm'])
    choice = ImCheck(tMysqlUpdate).lower()
    connect = "ssh -p{Port} {User}@{IP} ".format(
        Port=ServerPortN, User=UserN, IP=ServerIPN)
    cmdcrondel = connect + " \"sed -i /sbcl/d /etc/crontab \""
    if choice in rm:
        ChmyN = "NO"
        ChmyNReal = "NO"
    elif choice in yes:
        ChmyN = "YES"
        ChmyNReal = "YES"
        choicech = ImCheck(Text_Style(tCheckMy)).lower()
        if choicech in yes:
            pass
        else:
            print Text_Style(tPlconfMy)
            return
        cmdscp = "scp -P{Port} /usr/share/sbcl/sbcl {User}@{IP}:/usr/sbin/".format(Port=ServerPortN,
                                                                                   User=UserN, IP=ServerIPN)
        cmddb = connect + " \"mysql -e 'show databases;'\""
        cmddf = connect + " \"df -h\""
        print tResdf
        os.system(cmddf)
        if DirsInc == "Empty":
            DirsIncExample = DirIncDef
        else:
            DirsIncExample = DirsInc
        DirsIncN = ImCheck(
            tDirBInc + ExampleIncDir + ' [ Now:' + DirsInc + ' ]: ',
            default=DirsIncExample )
        print (Text_Style(tUdb))
        os.system(cmddb)
        print (Text_Style(tAOS))
        if DBex == "Empty":
            DBexExample = DBexDef
        else:
            DBexExample = DBex
        DBexN = ImCheck(tDBex + ExampleExDB +
                        '[Now: ' + DBex + ']: ', default=DBexExample,  Empty="YES")
        if MyDumpOpt == "Empty":
            MyDumpOptExample = MysqlOptDef
        else:
            MyDumpOptExample = MyDumpOpt
        MyDumpOptN = ImCheck(tMyDumpOpt + tDefMysqlOpt +
                             '[Now:' + MyDumpOpt + ']:', default=MyDumpOptExample, Space = "True")
        CronN = ImCheck(tSbcltext + tSbclCron + tSbcltext2, default=tSbclCron, Space = "True")
        cmdcron = connect + " \"echo '" + CronN + "' >> /etc/crontab\""
    else:
        pass
    if CronN is not None:
        print CronN + tAddtoCron
    if CronN is None and ChmyN == "NO":
        MyDumpOptN = "Empty"
        DirsIncN = "Empty"
        DBexN = "Empty"
        MysqlReadyN = "Empty"
    else:
        pass
    print Text_Style(tDesc + Desc)
    DescN = ImCheck(
        tDescrm,  default=Desc, Empty="YES", Space="True" )
    if DescN == "rm": DescN = ""
    choice = ImCheck(tDataCor).lower()
    if choice in yes:
        # print id
        data = {"Name":  ServerNameN, "User": UserN,  "ServerIP": ServerIPN, "ServerPort": ServerPortN,
                "RsyncOpt": RsyncOptN, "Dirs": DirsN, "DirsExclude": DirsExcludeN, "Priv": PrivN,
                "Frequency": FrequencyN, "CleanDate": CleanDateN, "DirsInc": DirsIncN, "DBex": DBexN,
                "MyDumpOpt": MyDumpOptN,  "Chmy": ChmyN, "MysqlReady": MysqlReadyN, "Desc": DescN}

        SB.coll.update({'_id': id}, {"$set": data}, upsert=False)
        if ChmyNReal == "YES":
            os.system(cmdscp)
            os.system(cmdcrondel)
            os.system(cmdcron)
        elif ChmyNReal == "NO":
            os.system(cmdcrondel)
            print tDelCronResult
        else:
            pass
        print Text_Style(tEndofUpdate)
    elif choice in no:
        print tBye
        return sys.exit(1)
    else:
        sys.stdout.write(tPlease)


def add():
    print Text_Style(tNote)
    #import time
    # time.sleep(3)
    yes = set(['yes', 'y', 'ye'])
    no = set(['no', 'n'])
    choicech = ImCheck(tCheckRsync).lower()
    if choicech in yes:
        pass
    else:
        print Text_Style(tPlInR)
        return
    ServerName = ImCheck(tServName)
    ServerIP = ImCheckIP(tServIP)
    User = ImCheck(tUser + Defroot, default=UserDef)
    ServerPort = ImCheck(tServPort + Defport,  default=PortDef)
 #   ServerPort = ServerPort.replace(' ', '')
    RsyncOpt = ImCheck(tOpR + Defop, default=RsyncOptDef, Space = "True")
    Priv = ImCheck(tPriy + Defpri,  default=PrivDef)
    Dirs = ImCheck(tDirB + ExampleDir + ": ",  default=DirsDef)
    DirsExclude = ImCheck(
        tDirBx + ExampleDirEx + ": ",  default='',  Empty="YES")
    Frequency = ImCheck(tFB + DefFr,  default=FrequencyDef)
    CleanDate = ImCheck(tCleanB + DefClean,  default=CleanDateDef)
    # PrCheck(ServerName, User,  ServerIP, ServerPort,
    #        RsyncOpt, Priv, Dirs, DirsExclude, Frequency, CleanDate)
    choice = ImCheck(tDataCor).lower()
    if choice in yes:
        print Text_Style(tAddsshKey)
        # time.sleep(3)
        connect = "ssh -p{Port} {User}@{IP} ".format(
            Port=ServerPort, User=User, IP=ServerIP)
        cmd = "cat " + SB.PublickKey + " | " + connect + \
            " \"mkdir -p ~/.ssh && cat >>  ~/.ssh/authorized_keys\""
        cmdscp = "scp -P{Port} /usr/share/sbcl/sbcl {User}@{IP}:/usr/sbin/".format(Port=ServerPort,
                                                                                   User=User, IP=ServerIP)
        cmdscpini = "scp -P{Port} /usr/share/sbcl/sbcl.ini {User}@{IP}:/etc/sbcl/".format(Port=ServerPort,
                                                                                   User=User, IP=ServerIP)
        cmdmkini = connect + "\"mkdir -p /etc/sbcl\""
        cmdmklog = connect + "\"mkdir -p /var/log/sbclient\""
        os.system(cmdmkini)
        os.system(cmdmklog)
        os.system(cmd)
        os.system(cmdscp)
        os.system(cmdscpini)
        choise = ImCheck(tDoUBackupMysql).lower()
        if choise in yes:
            choicech = ImCheck((Text_Style(tCheckMy))).lower()
            if choicech in yes:
                pass
            else:
                print Text_Style(tPlconfMy)
                return
            Chmy = "YES"
            cmd = connect + " \"df -h\""
            print tResdf
            os.system(cmd)
            DirsInc = ImCheck(
                tDirBInc + '[default /var/backup]: ', default=DirIncDef)
            cmdmk = connect + "\"mkdir -p {dir}\"".format(dir=DirsInc)
            cmdmklog = connect + "\"mkdir -p /var/log/sbclient\""
            choice = ImCheck(tDoUexdb).lower()
            if choice in yes:
                cmd = connect + " \"mysql -e 'show databases;'\""
                print Text_Style(tUdb)
                os.system(cmd)
                print (Text_Style("##############"))
                DBex = ImCheck(tDBex + tdefExDb,
                               default=DBexDef,  Empty="YES")
            else:
                DBex = "Empty"
            MyDumpOpt = ImCheck(tMyDumpOpt + tDefMysqlOpt, default=MysqlOptDef, Space = "True")
            Cron = ImCheck(tSbcltext + tSbclCron +
                           tSbcltext2, default=tSbclCron,  Space = "True" )
            cmdcron = connect + " \"echo '" + Cron + "' >> /etc/crontab\""
        else:
            Chmy = "NO"
            MyDumpOpt = "Empty"
            DirsInc = "Empty"
            DBex = "Empty"
        serv = "^" + ServerName + "$"
        Desc = ImCheck(
        tDesc,  default='',  Empty="YES", Space="True")
        MongoIn(ServerName, User, ServerIP, ServerPort, RsyncOpt,
                Priv, Dirs, DirsExclude, Frequency, CleanDate, Chmy, MyDumpOpt, DirsInc, DBex, Desc )
        if Chmy == "YES":
            os.system(cmdmk)
            print tInstClient
            os.system(cmdcron)
        MongoList(pattern={"Name": {'$regex': serv}})
    elif choice in no:
        print tBye
        return
    else:
        sys.stdout.write(tPlease)


def Delete(Name):
    SB.MongoCon()
    allservers = list(SB.coll.find({"Name": Name}))
    List(allservers)
    if count == 0:
        return
    #PrCheck(ServerName,ServerIP,ServerPort, RsyncOpt,Priv,Dirs, DirsExclude )
    yes = set(['yes', 'y', 'ye'])
    no = set(['no', 'n'])
    choice = ImCheck(Text_Style(tDuD)).lower()
    if choice in yes:
        SB.coll.remove({'_id': id})
        choice = ImCheck(Text_Style(tDuDel + SB.DirBackup +
                                "/" + ServerName + " ")).lower()
        if choice in yes:
            cmd = "rm -fr {dir}".format(dir=SB.DirBackup + "/" + ServerName)
            os.system(cmd)
    elif choice in no:
        print tBye
    else:
        sys.stdout.write(tPlease)


def Command(Serv, Args):
    MongoList(pattern={"Name": Serv})
    try:
        connect = "ssh -p{Port} {User}@{IP} ".format(
            Port=ServerPort, User=User, IP=ServerIP)
        cmd = connect + "\"" + Args + "\""
        return os.system(cmd)
    except:
        return

def UpdateCl():
    SB.MongoCon()
    allservers = list(SB.coll.find({}))
    for R in allservers:
        ServerName = R['Name']
        User = R['User']
        IP = R['ServerIP']
        Port = R['ServerPort']
        print tUpdateCl + ServerName
        cmd="scp -P{port} /usr/share/sbcl/sbcl {user}@{ip}:/usr/sbin/".format(user=User, 
                                                                            port=Port, ip=IP)
        os.system(cmd)
    


def Status(Name, Stat):
    SB.MongoCon()
    allservers = list(SB.coll.find({"Name": Name}))
    List(allservers)
    if Stat == "Done":
        Value = "Done"
    elif Stat == "Disabled":
        Value = "Disabled"
    elif Stat == "needbackup":
        Value = "needbackup"
    else:
        return tUsestat
    data = {"Status": Value}
    SB.coll.update({'_id': id}, {"$set": data}, upsert=False)
    return tStatdone


def MongoFindParm(Parm, Obj, regex):
    if regex == "find-regex":
        Obj = {'$regex': Obj}
    elif regex == "find-not":
        Obj = {'$ne':  Obj}
    SB.MongoCon()
    allservers = list(SB.coll.find({Parm: Obj}))
    return List(allservers)


def FindHelp():
    return """\n\tUsing """ + Text_Style("find/find-not/find-regex") + """ with keys
    \t""" + tServName + Text_Style("\tName") + """
    \t""" + tServIP + Text_Style("\tServerIP") + """
    \t""" + tUser + Text_Style("\t\tUser") + """
    \t""" + tServPort + Text_Style("\tServerPort") + """
    \t""" + tPriy + Text_Style("\t\tPriv") + """
    \t""" + tOpR + Text_Style("\tRsyncOpt") + """
    \t""" + tStatus + Text_Style("\t\tStatus") + """
    \t""" + tLastD + Text_Style("\tDateStart") + """
    \t""" + tLastDN + Text_Style("\tDateEnd") + """
    \t""" + tDirB + Text_Style("\tDirs") + """
    \t""" + tDirBx + Text_Style("\tDirsExclude") + """
    \t""" + tFB + Text_Style("\tFrequency") + """
    \t""" + tCleanB + Text_Style("\tCleanDate") + """
    \t""" + tChmy + Text_Style("\t\tChmy") + """
    \t""" + tDirBInc + Text_Style("\tDirsInc") + """
    \t""" + tDBex + Text_Style("\tDBex") + """
    \t""" + tMyDumpOpt + Text_Style("\tMyDumpOpt") + """
    \t""" + tMysqlReady + Text_Style("\tMysqlReady") + """
    \t""" + tMysqlLog   + Text_Style("\tMysqlLog") + """
    \t""" + tDateStartMysql + Text_Style("\tDateStartMysql") + """
    \t""" + tDateStopMysql + Text_Style("\tDateStopMySQL") + """
    \n
    \tExamples: 
    \tlist all servers with status rsync error: """ + Text_Style("sbctl find Status \"rsync error\"") + """
    \tlist all servers with \"""" + tChmy + """NO\": """ + Text_Style("sbctl find Chmy NO") + """
    \n"""


def help():
    return """Version """+Version+"""
    \nHelp function: Basic Usage:
    \t""" + Text_Style("add", color="WHITE") + """ or addhost \t\t- Add host to backup
    \t""" + Text_Style("l", color="WHITE") + """ or  list     \t\t- List all hosts
    \t""" + Text_Style("se", color="WHITE") + """ or search   \t\t- Search for the host name, example: """ + Text_Style("sbctl search w1.host.com") + """
    \t""" + Text_Style("re", color="WHITE") + """ or reconf   \t\t- Reconfiguration of backup settings, example: """ + Text_Style("sbctl reconf w1.host.com") + """
    \t""" + Text_Style("rm", color="WHITE") + """ or remove   \t\t- Remove host, example: """ + Text_Style("sbctl delete w1.host.com") + """
    \t""" + Text_Style("ho", color="WHITE") + """ or host     \t\t- Send command to remote host, example: """ + Text_Style("sbctl host w1.host.com \"ls -al /var/backup\"") + """
    \t""" + Text_Style("backup", color="WHITE") + """         \t\t- Start backup, example: """ + Text_Style("sbctl backup w1.host.com") + """
    \t""" + Text_Style("update-sbcl", color="WHITE") + """    \t\t- Update clinet, example: sbctl update-sbcl
    \t""" + Text_Style("status", color="WHITE") + """         \t\t- Status update, example: """ + Text_Style("sbctl status w1.host.com Done/Disabled/needbackup") + """
    \t   status Done         \t- Backup is done
    \t   status Disabled     \t- Turn backup off
    \t   status needbackup   \t- Need to backup
    \t""" + Text_Style("find", color="WHITE") + """           \t\t- List the hosts matching parameters, example: """ + Text_Style("sbctl find Status \"rsync error\"") + """
    \t""" + Text_Style("find-not", color="WHITE") + """       \t\t- List the hosts invert-matching parameters, example: """ + Text_Style("sbctl find-not Chmy YES") + """
    \t""" + Text_Style("find-regex", color="WHITE") + """     \t\t- Use regular expression to find the hosts on their parameter, example: """ + Text_Style("sbctl find-regex Status error") + """ 
    \t""" + Text_Style("find help", color="WHITE") + """     \t\t- List all parameter keys, example: """ + Text_Style("sbctl find help") + """ 
    \t""" + FindHelp() + """
    \thelp              \t\t- Help
    \n"""


def main():
    try:
        argv = sys.argv[1]
        if argv == 'addhost' or argv == 'add':
            add()
        elif argv == 'list' or argv == 'l':
            MongoList()
        elif argv == 'search' or argv == 'se':
            MongoList(pattern={"Name": {'$regex': sys.argv[2]}})
        elif argv == 'reconf' or argv == 're':
            MongoUpdate(sys.argv[2])
        elif argv == 'remove' or argv == 'rm':
            Delete(sys.argv[2])
        elif argv == 'host' or argv == 'ho':
            Command(sys.argv[2], sys.argv[3])
        elif argv == "backup":
            cmd = "sbd backup " + sys.argv[2]
            os.system(cmd)
        elif argv == "status":
            try:
                print Status(sys.argv[2], sys.argv[3])
            except:
                pass
        elif argv == "find" or argv == "find-regex" or argv == "find-not":
            if sys.argv[2] == "help":
                print FindHelp()
            else:
                MongoFindParm(sys.argv[2], sys.argv[3], regex=argv)
        elif argv == "update-sbcl":
            UpdateCl()
        else:
            print help()
    except IndexError:
        print help()
    except EOFError:
        print Text_Style(tBye)


if __name__ == '__main__':
    main()
