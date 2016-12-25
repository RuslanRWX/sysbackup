#!/usr/bin/python
import os
import threading
import Queue
import time, random

MongoConnect='localhost:27017'
DBs="ServersBackup"
Collection="servers"
Num_thread = 2
DIR="/home/ruslan/ruslan/SB"

def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(MongoConnect)
    coll = cl[DBs][Collection]
    
def CreateTmpFiles(Name,  Dirs, DirsEx):
    Dirs=Dirs.replace(',', '\n')  + "\n"
    DirsEx=DirsEx.replace(',', '\n') + "\n"
    FileNameIn=DIR  + "/tmp/" + Name +"_inc.txt"
    FileNameEx=DIR +"/tmp/"+ Name +"_ex.txt"
    FileIn=open(FileNameIn,  "w" )
    FileIn.write(Dirs)
    FileIn.close()
    FileEx=open(FileNameEx,  "w" )
    FileEx.write(DirsEx)
    FileEx.close()
    

def Backup(Server):
    import datetime
    MongoCon()
    Mq=coll.find()
    from random import randint
    from time import sleep
    SL=(randint(1,20))
    ServerData = list(coll.find({ "Name": Server}))
    ts = time.time()
    ISODateStart = datetime.datetime.now().isoformat()
    for R in ServerData:
        CreateTmpFiles(R["Name"],  R["Dirs"], R["DirsExclude"])
        id=R['_id']
        print "##########################\n"
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
        
        
    
 #   dataUp = { "Name" :  Server ,  "DataStart" :  new ISODate() }
 #   coll.update({'_id':id}, {"$set": dataUp}, upsert=False)
 #   print Server +" Sleep Start backup"+ str(SL) +"\n"
 #   for R in ServersData:
 #       print "##########################\n"
#        print  "Server name: "+ R['Name']
#        print  "Server IP: ",  R['ServerIP']
  #      print  "Server port: ",  R['ServerPort']
 #       print  "Options of rsync: "+ R['RsyncOpt'] +"\n"
    #print Server
    #time.sleep(5)
    time.sleep(SL)


#def CreateQ():
 #   MongoCon()
  #  AllServers=list(coll.find())
#    global Servers
#    Servers=[]
#  for R in AllServers:
#        Servers.append(R["Name"])
#   return Servers

class Worker(threading.Thread):

    def __init__(self, queue):
        self.__queue = queue
        threading.Thread.__init__(self)

    def run(self):
        while 1:
            item = self.__queue.get()
            if item is None:
                break # reached end of queue

            # pretend we're doing something that takes 10-100 ms
            #time.sleep(random.randint(10, 100) / 1000.0)
            tc=threading.activeCount()
            print "active threads "+ str(tc)
            Backup(item)

def CreateQ():
    ServersQ={}
    MongoCon()
    Mq=coll.find().sort('Priv',  1)
    allservers = list(Mq)
    return allservers
    
def worker():
    while True:
        item = q.get()
        Backup(item)
        q.task_done()

def Q():
    global q
    q = Queue.Queue(0)
    for i in range(Num_thread):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    for item in CreateQ():
        q.put(item["Name"])
    q.join()  




def main ():
    #while True:
    Q()
    #Name="Server"
    #D="/home/,/Dowload"
    #E="/Log/,/var/*"
    #CreateTmpFiles(Name, D, E)

if __name__ == '__main__':
    main()
