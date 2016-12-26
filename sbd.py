#!/usr/bin/python
import ConfigParser,  os
import threading
import Queue
import time, random
import sys
sys.path.insert(0, "lib")
import  SB

def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(SB.MongoConnect)
    coll = cl[SB.DBs][SB.Collection]

def CreateTmpFiles(Name,  Dirs, DirsEx):
    Dirs=Dirs.replace(',', '\n')  + "\n"
    DirsEx=DirsEx.replace(',', '\n') + "\n"
    FileNameIn=SB.DIR  + "/tmp/" + Name +"_inc.txt"
    FileNameEx=SB.DIR +"/tmp/"+ Name +"_ex.txt"
    FileIn=open(FileNameIn,  "w" )
    FileIn.write(Dirs)
    FileIn.close()
    FileEx=open(FileNameEx,  "w" )
    FileEx.write(DirsEx)
    FileEx.close()

class Backup:
    def __init__(self, S):
        self.Server = S

    def run(self):
        import datetime
        MongoCon()
        Mq=coll.find()
        Server=self.Server
        from random import randint
        from time import sleep
        SL=(randint(1,20))
        ServerData = list(coll.find({ "Name": Server}))
        ts = time.time()
        ISODateStart = datetime.datetime.now().isoformat()
        for R in ServerData:
            CreateTmpFiles(R["Name"],  R["Dirs"], R["DirsExclude"])
            id=R['_id']
            print "###########Start Backup############\n"
            print  "Server name: "+ R['Name']
            print  "Server IP: ",  R['ServerIP']
            print  "Server port: ",  R['ServerPort']
            print  "Options of rsync: "+ R['RsyncOpt'] +"\n"
            print  " Sleep Start backup  "+ str(SL) +"\n"
            DateUp={ "DateStart" : ISODateStart }
            coll.update({'_id':id}, {"$set": DateUp}, upsert=False)
            time.sleep(SL)
            ISODateEnd = datetime.datetime.now().isoformat()
            DateUp={ "DateEnd" : ISODateEnd }
            coll.update({'_id':id}, {"$set": DateUp}, upsert=False)
        time.sleep(SL)

def CreateQ():
    ServersQ={}
    MongoCon()
    Mq=coll.find().sort('Priv',  1)
    allservers = list(Mq)
    return allservers
    
def worker():
    while True:
        item = q.get()
        Back=Backup(item)
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


def main ():
    #sbmain.Conf()
    #test()
    #while True:
     Q()
    #Name="Server"
    #D="/home/,/Dowload"
    #E="/Log/,/var/*"
    #CreateTmpFiles(Name, D, E)

if __name__ == '__main__':
    main()
