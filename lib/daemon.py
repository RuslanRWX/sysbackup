#!/usr/bin/python
# SySBackup deamon libs

import sys
import time
import datetime
import os
import re
sys.path.append(".")
import SB


def log(text, file):
    logf = open(file, "a")
    logf.write(text)
    logf.close()


def check():
    tmp = SB.tmp
    LogDir = SB.LogDir
    DirBackup = SB.DirBackup
    SB.MongoCon()
    result = list(SB.collCluster.find({"Node": SB.Node }))
    if result == [] or result[0]["Node"] == "":
        text = "Add node to MongoDB\n"
        log(text, SB.Log)
        data = [{"Node": SB.Node}]
        SB.collCluster.insert(data, True)
    del result
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
        file(SB.Pidfile, 'w').write(SB.pid)


def create_queue():
    ServersQ = {}
    SB.MongoCon()
    Mq = SB.coll.find({"Status": {"$ne": "Disabled"}, "NodeName": SB.Node}).sort("Priv",  1)
    servers = list(Mq)
    return servers

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


def create_tmp_file(Name, DirsEx):
    DirsEx = DirsEx.replace(' ', '')
    DirsEx = DirsEx.replace(',', '\n') + "\n"
    FileNameEx = SB.tmp + "/" + Name + "_ex.txt"
    FileEx = open(FileNameEx, "w")
    FileEx.write(DirsEx)
    FileEx.close()

def date_check(checkdate):
    checkdate = int(checkdate)
    date0 = datetime.datetime.now() - datetime.timedelta(hours=checkdate)
    date = date0.isoformat()
    return date


class backup_function:
    def __init__(self, S, Not_check="NO"):
        self.Server = S
        self.Not_check = Not_check
        SB.MongoCon()
        self.CodeRsync = None
        SD = list(SB.coll.find({"Name": self.Server}))
        for R in SD:
            self.Name = R["Name"]
            self.CleanDate = R["CleanDate"]
            self.Frequency = R["Frequency"]
            self.DirsExclude = R["DirsExclude"]
            self.Dirs = R["Dirs"]
            self.User = R["User"]
            self.id = R["_id"]
            self.ServerIP = R["ServerIP"]
            self.ServerPort = R["ServerPort"]
            self.RsyncOpt = R["RsyncOpt"]
            self.Dirs = R["Dirs"]
            self.Dirs = R["Dirs"]
            self.DirsExclude = R["DirsExclude"]
            self.DateStart = R["DateStart"]
            self.DateEnd = R["DateEnd"]
            self.DirsInc = R["DirsInc"]
            self.Chmy = R["Chmy"]
            self.Status = R["Status"]
            self.MysqlReady = R["MysqlReady"]
        self.ISODateStart = datetime.datetime.now().isoformat()
        self.chdate = date_check(self.Frequency)
        if self.Chmy == "YES":
            self.DirsExclude = self.DirsExclude + "," + self.DirsInc
        if self.Chmy == "YES" and self.Not_check == "YES":
            backup_function.mysqldump(self.Server)
        create_tmp_file(self.Name, self.DirsExclude)
        self.DirB = SB.DirBackup + "/" + self.Name
        self.DirBL = SB.DirBackup + "/" + self.Name + "/" + self.ISODateStart
        self.ExFile = SB.tmp + "/" + self.Name + "_ex.txt"
        self.Link = self.DirB + "/" + "Latest"

    def skip_backup(self):
        if self.DateEnd > self.chdate and \
                        self.Not_check == "NO" and self.Status == "Done":
            return 1
        elif  self.DateEnd > self.chdate and \
                        self.Status == "rsync error":
            return 1
        elif self.Status == "running":
            tbackuprun = self.Name + " Backup already running"
            log(tbackuprun, SB.Log)
            return 1
        elif self.MysqlReady == "NO" and self.Chmy == "YES":
            text = "\n" + self.Name + ": Mysqldump is not ready"
            log(text, SB.Log)
            print text
            return

    def mysqldump(self):
            cmd = "sbctl host " + \
                      self.Server + " \"/usr/sbin/sbcl mysqldump\""
            os.system(cmd)
            time.sleep(3)

    def start_log(self):
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
        text = text.format(time=datetime.datetime.now(),
                    name=self.Name, user=self.User, ip=self.ServerIP,
                        port=self.ServerPort, rsyncOpt=self.RsyncOpt, dirs=self.Dirs,
                           dirE=self.DirsExclude, dateS=self.DateStart)
        log(text, SB.Log)

    def update_status_start(self):
        self.ISODateStart = datetime.datetime.now().isoformat()
        Data = {"DateStart": self.ISODateStart,
                  "Status": "running", "DateEnd": ""}
        SB.coll.update({'_id': self.id}, {"$set": Data}, upsert=False)

    def update_status_end(self, status):
        self.ISODateEnd = datetime.datetime.now().isoformat()
        Data = {"DateEnd": self.ISODateEnd, "Status": status}
        SB.coll.update({'_id': self.id}, {"$set": Data}, upsert=False)

    def create_path(self):
        if not os.path.exists(self.DirB):
            os.makedirs(self.DirB)
        if not os.path.exists(self.DirBL):
            os.makedirs(self.DirBL)

    def create_rsync_dirs(self):
        cmd=[]
        for RD in self.Dirs.split(","):
            if RD != "/":
                RD = re.sub(r'\/$', '', RD)
        cmd.append("/usr/bin/rsync  {rsopt} --relative --log-file={logdir}/{serv}.log --progress" \
                   " -e \"/usr/bin/ssh -p {port}\"  --delete  --timeout=600 --ignore-errors --exclude-from={exf}" \
                   " --link-dest={dir}/Latest {user}@{ip}:{rd}  {dirbl} ".format(rsopt=self.RsyncOpt,
                                                                                 port=self.ServerPort,
                                                                                 exf=self.ExFile,
                                                                                 dir=self.DirB,
                                                                                 user=self.User,
                                                                                 ip=self.ServerIP,
                                                                                 rd=RD,
                                                                                 dirbl=self.DirBL,
                                                                                 logdir=SB.LogDir,
                                                                                 serv=self.Name))
        return cmd

    def rsync_dirs(self, dirs):
        for dir in dirs:
            code = os.system(dir)
            if code > 0:
                log(self.Name + " rsync error!\n", SB.LogError)
                self.CodeRsync = "1"

    def create_rsync_mysql_dir(self):
        cmd = "/usr/bin/rsync  {rsopt} --relative --log-file={logdir}/{serv}.log --progress " \
                            "-e \"/usr/bin/ssh -p {port}\" --timeout=600 --ignore-errors {user}@{ip}:{rd} " \
                            " {dirbl} ".format(rsopt=self.RsyncOpt,
                                               port=self.ServerPort,
                                               exf=self.ExFile,
                                               dir=self.DirB,
                                               user=self.User,
                                               ip=self.ServerIP,
                                               rd=self.DirsInc,
                                               dirbl=self.DirBL,
                                               logdir=SB.LogDir,
                                               serv=self.Name)
        return cmd

    def rsync_mysql_dir(self, dir):
        code = os.system(dir)
        if code > 0:
            log(self.Name + " rsync error, mysql directory!\n", SB.LogError)
            self.CodeRsync = "1"

    def remove_link(self):
        try:
            os.remove(self.Link)
            time.sleep(3)
        except:
            pass

    def create_status(self):
        if self.CodeRsync is not None:
            Status = "rsync error"
        else:
            Status = "Done"
        return Status

    def end_text(self):
        text = """\n############ End Backup  #######
        Now TIME: {time}
        Server name: {name}
        DateEnd : {date}"""
        text = text.format(time=datetime.datetime.now(),
                           name=self.Name, date=self.DateEnd)
        log(text, SB.Log)

    def clean_local_store(self):
        Drs = set()
        rDir = os.listdir(self.DirB)
        CleanD = int(self.CleanDate) * 24
        DCh = date_check(CleanD)
        for rd in rDir:
            Drs.add(rd)
        Drs.discard("Latest")
        resultDir = filter(lambda x: DCh > x, Drs)
        if resultDir != []:
            for D in resultDir:
                path = self.DirB + "/" + D
                # print path
                cmdrm = "/bin/rm -rf {p}".format(p=path)
                os.system(cmdrm)


class backup:
    def __init__(self, S):
        self.Server = S
        self.bf=backup_function(self.Server)
        self.skip_backup = self.bf.skip_backup()

    def run(self):
        if self.skip_backup == 1:
            return
        self.bf.start_log()
        self.bf.update_status_start()
        self.bf.create_path()

        path_dirs=self.bf.create_rsync_dirs()
        self.bf.rsync_dirs(path_dirs)
        if self.bf.Chmy == "YES":
            path_dir_mysql=self.bf.create_rsync_mysql_dir()
            self.bf.rsync_mysql_dir(path_dir_mysql)
        self.bf.remove_link()
        os.symlink(self.bf.DirBL, self.bf.Link)
        Status=self.bf.create_status()
        self.bf.update_status_end(Status)
        self.bf.end_text()
        self.bf.clean_local_store()



