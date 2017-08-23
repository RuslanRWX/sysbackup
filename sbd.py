#!/usr/bin/python
# SySBackup deamon
# Copyright (c) 2017 Ruslan Variushkin,  ruslan@host4.biz
Version = "0.4.0"


import os
import threading
import Queue
import time
import sys
import datetime
pid = str(os.getpid())
import re
#sys.path.append("lib/")
import SB


def CreateTmpFiles(Name, DirsEx):
    DirsEx = DirsEx.replace(' ', '')
    DirsEx = DirsEx.replace(',', '\n') + "\n"
    FileNameEx = SB.tmp + "/" + Name + "_ex.txt"
    FileEx = open(FileNameEx,  "w")
    FileEx.write(DirsEx)
    FileEx.close()


def DateCheck(checkdate):
    checkdate = int(checkdate)
    # print checkdate
    date0 = datetime.datetime.now() - datetime.timedelta(hours=checkdate)
    date = date0.isoformat()
    #dateCh = "%s000000" % (date)
    return date


def log(text, file):
    logf = open(file, "a")
    logf.write(text)
    logf.close()


class Backup:
    def __init__(self, S, Not_check="NO"):
        self.Server = S
        self.Not_check = Not_check

    def run(self):
        SB.MongoCon()
        Mq = SB.coll.find()
        Server = self.Server
        CodeRsync = None
        SD = list(SB.coll.find({"Name": Server}))
        for R in SD:
            Name = R["Name"]
            CleanDate = R["CleanDate"]
            Frequency = R["Frequency"]
            DateEnd = R["DateEnd"]
            DirsExclude = R["DirsExclude"]
            Dirs = R["Dirs"]
            User = R["User"]
            id = R["_id"]
            ServerIP = R["ServerIP"]
            ServerPort = R["ServerPort"]
            RsyncOpt = R["RsyncOpt"]
            Dirs = R["Dirs"]
            Dirs = R["Dirs"]
            DirsExclude = R["DirsExclude"]
            DateStart = R["DateStart"]
            DirsInc = R["DirsInc"]
            Chmy = R["Chmy"]
            Status = R["Status"]
        ISODateStart = datetime.datetime.now().isoformat()
        chdate = DateCheck(Frequency)
        if DateEnd > chdate and self.Not_check == "NO" and Status == "Done" or DateEnd > chdate and Status == "rsync error":
            return
        if Status == "running":
            tbackuprun = Name + " Backup already running"
            log(tbackuprun, SB.Log)
            print tbackuprun
        if Chmy == "YES":
            DirsExclude = DirsExclude + "," + DirsInc
        if Chmy == "YES" and self.Not_check == "YES":
            cmdsbcl = "sbctl host " + \
                sys.argv[2] + " \"/usr/sbin/sbcl mysqldump\""
            os.system(cmdsbcl)
            time.sleep(3)
        if R["MysqlReady"] == "NO" and Chmy == "YES":
            text = "\n" + Name + ": Mysqldump is not ready"
            log(text, SB.Log)
            print text
            return
        CreateTmpFiles(Name, DirsExclude)
        text = """\n########### Start Backup ######
        Now TIME: {time}
        Server name: {name}
        User: {user}
        Server IP: {ip}
        Server port: {port}
        Options of rsync: {rsyncOpt}
        Dirs : {dirs}
        Dirs exclude: {dirE}
        DateStart : {dateS}\n"""
        text = text.format(time=datetime.datetime.now(), name=Name, user=User, ip=ServerIP,
                           port=ServerPort, rsyncOpt=RsyncOpt, dirs=Dirs, dirE=DirsExclude, dateS=DateStart)
        log(text, SB.Log)
        DateUp = {"DateStart": ISODateStart,
                  "Status": "running", "DateEnd": ""}
        SB.coll.update({'_id': id}, {"$set": DateUp}, upsert=False)
        DirB = SB.DirBackup + "/" + Name
        DirBL = SB.DirBackup + "/" + Name + "/" + ISODateStart
        ExFile = SB.tmp + "/" + Name + "_ex.txt"
        # "Start rsync ! "
        if not os.path.exists(DirB):
            os.makedirs(DirB)
        if not os.path.exists(DirBL):
            os.makedirs(DirBL)
        for RD in Dirs.split(","):
            if RD != "/":
                RD = re.sub(r'\/$', '', RD)
            cmdrsync = "/usr/bin/rsync  {rsopt} --relative --log-file={logdir}/{serv}.log --progress -e \"/usr/bin/ssh -p {port}\"  --delete  --timeout=600 --ignore-errors --exclude-from={exf} --link-dest={dir}/Latest {user}@{ip}:{rd}  {dirbl} ".format(rsopt=RsyncOpt,
                                                                                                                                                                                                                                                             port=ServerPort, exf=ExFile, dir=DirB, user=User, ip=ServerIP, rd=RD, dirbl=DirBL, logdir=SB.LogDir, serv=Name)
            code = os.system(cmdrsync)
            if code > 0:
                log(Name + " rsync error!\n", SB.LogError)
                CodeRsync = "1"
        if Chmy == "YES":
            cmdrsyncmysql = "/usr/bin/rsync  {rsopt} --log-file={logdir}/{serv}.log --progress -e \"/usr/bin/ssh -p {port}\" --timeout=600 --ignore-errors {user}@{ip}:{rd}  {dirbl} ".format(rsopt=RsyncOpt,
                                                                                                                                                                                              port=ServerPort, exf=ExFile, dir=DirB, user=User, ip=ServerIP, rd=DirsInc, dirbl=DirBL, logdir=SB.LogDir, serv=Name)
            code = os.system(cmdrsyncmysql)
            if code > 0:
                log(Name + " rsync error, mysql directory!\n", SB.LogError)
                CodeRsync = "1"
        # print DirBL
        # print DirB
        Link = DirB + "/" + "Latest"
        try:
            os.remove(Link)
            time.sleep(3)
        except:
            pass
        #link="ln -s {dir} {lin}".format(dir=DirBL, lin=Link)
        os.symlink(DirBL, Link)
        # os.system(link)
        if CodeRsync is not None:
            Status = "rsync error"
        else:
            Status = "Done"
        ISODateEnd = datetime.datetime.now().isoformat()
        DateUp = {"DateEnd": ISODateEnd, "Status": Status}
        SB.coll.update({'_id': id}, {"$set": DateUp}, upsert=False)
        text = """\n############ End Backup  #######
        Now TIME: {time}
        Server name: {name}
        DateEnd : {date}"""
        text = text.format(time=datetime.datetime.now(),
                           name=Name, date=DateEnd)
        log(text, SB.Log)
        # cmdclean = "/usr/bin/find %s -maxdepth 1 -mtime +%s -exec rm -r '{}' \;" % (
        #    DirB, CleanDate)
        Drs = set()
        rDir = os.listdir(DirB)
        CleanD = int(CleanDate) * 24
        # print CleanDate
        # print CleanD
        DCh = DateCheck(CleanD)
        for rd in rDir:
            Drs.add(rd)
        Drs.discard("Latest")
        resultDir = filter(lambda x: DCh > x, Drs)
        # print "Start check dir"
        # print "Chekc date:",  DCh
        if resultDir != []:
            for D in resultDir:
                path = DirB + "/" + D
                # print path
                cmdrm = "/bin/rm -rf {p}".format(p=path)
                os.system(cmdrm)
        #text="\nStart clean the back            print Rup server\nCommand: {com}".format(com=cmdclean)
        # log(text)


def CreateQ():
    ServersQ = {}
    SB.MongoCon()
    Mq = SB.coll.find({"Status": {"$ne": "Disabled"}}).sort('Priv',  1)
    allservers = list(Mq)
    return allservers


def API():
    import socket
    import pickle
    SERVER_ADDRESS = SB.IP
    SERVER_PORT = int(SB.Port)
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((SERVER_ADDRESS, SERVER_PORT))
    s.listen(255)
    print("Listening on address %s." %
          str((SERVER_ADDRESS, SERVER_PORT)))
    while True:
        c, addr = s.accept()
        print("\nConnection received from %s" % str(addr))
        try:
            while True:
                SB.MongoCon()
                data = c.recv(2048)
                if not data:
                    print("End of file from client. Resetting")
                    break
                data = data.decode()
                data = data.split("|")
                # print data
                print("Received '%s' from client " % data[0], str(addr))
                if data[0] == "Get":
                    DataMongo = list(SB.coll.find({"ServerIP": addr[0]}))
                    for R in DataMongo:
                        DataResult = R[data[1]]
                        if type(DataResult) == int:
                            DataResult = str(DataResult)
                        if DataResult == "":
                            DataResult = "Empty"
                elif data[0] == "Add":
                    DateUp = {data[1]: data[2]}
                    SB.coll.update({"ServerIP": addr[0]}, {
                                   "$set": DateUp}, upsert=False)
                    DataResult = "End"
                elif data[0] == "GetAll":
                    DataResult = list(SB.coll.find({"ServerIP": addr[0]}))
                else:
                    DataResult = "Error api: "
                DataResult = pickle.dumps(DataResult).encode()
                c.send(DataResult)
            c.close()
        except:
            pass


def worker():
    while True:
        item = q.get()
        Back = Backup(item)
        Back.run()
        q.task_done()


def Q():
    global q
    q = Queue.Queue(0)
    for i in range(SB.Num_thread):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    for item in CreateQ():
        q.put(item["Name"])
    q.join()


def Check():
    tmp = SB.tmp
    LogDir = SB.LogDir
    DirBackup = SB.DirBackup
    if not os.path.exists(tmp):
        os.makedirs(tmp)
    if not os.path.exists(LogDir):
        os.makedirs(LogDir)
    if not os.path.exists(DirBackup):
        os.makedirs(DirBackup)
    if os.path.isfile(SB.Pidfile):
        text = "\n{pd} already exists, exiting \n".format(pd=SB.Pidfile)
        log(text, SB.Log)
        print text
        return sys.exit(1)
    else:
        file(SB.Pidfile, 'w').write(pid)


def help():
    return """Help function: Basic Usage:\n
    \tstart      - Start the sbd deamon
    \tstop       - Stop the sbd deamon
    \trestart    - Restart the sbd deamon
    \tbackup     - Start backup just one node, example [sbd backup myhost] 
    \thelp       - Print help\n"""


def Stop():
    text = "\nStoped sbd {date}\n".format(date=datetime.datetime.now())
    log(text, SB.Log)
    print text
    if os.path.isfile(SB.Pidfile):
        f = open(SB.Pidfile, "r")
        PID = int(f.read())
        os.system('/usr/bin/pkill -TERM -P {pid}'.format(pid=PID))
        os.remove(SB.Pidfile)
        os.system('/usr/bin/pkill rsync')
        f.close()
        SB.MongoCon()
        DateUp = {"Status": "Stopped"}
        SB.coll.update({"Status": "running"}, {"$set": DateUp}, upsert=False)
        print "sbd is stopped"
    else:
        print "sbd is not running"


def Start():
    text = "\nStart sbd version:{ver}, date: {date}\n".format(
        ver=Version, date=datetime.datetime.now())
    log(text, SB.Log)
    print text
    t = threading.Thread(target=API)
    t.daemon = True
    t.start()
    while True:
        text = "\nStart queue, date: {date}".format(
            date=datetime.datetime.now())
        log(text, SB.Log)
        Q()
        text = "\nQueue is done, date: {date}\n".format(
            date=datetime.datetime.now())
        log(text, SB.Log)
        time.sleep(SB.TimeCheck)


def main():
    try:
        if sys.argv[1] == 'start':
            Check()
            Start()
        elif sys.argv[1] == 'stop':
            Stop()
        elif sys.argv[1] == 'restart':
            Stop()
            Start()
        elif sys.argv[1] == 'backup':
            tmp = SB.tmp
            name = sys.argv[2]
            if not os.path.exists(tmp):
                os.makedirs(tmp)
            Back = Backup(name, Not_check="YES")
            try:
                Back.run()
            except:
                print "Error: have not host like " + sys.argv[2] + " !"
        else:
            print help()
    except IndexError:
        print help()


if __name__ == '__main__':
    main()
