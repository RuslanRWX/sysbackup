#!/usr/bin/python
import os
import threading
import Queue
import time, random

MongoConnect='localhost:27017'
DBs="ServersBackup"
Collection="servers"
Num_thread = 2


def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(MongoConnect)
    coll = cl[DBs][Collection]
    
    
def Backup(Server):
    from random import randint
    from time import sleep
    SL=(randint(1,20))
    print Server +" Sleep "+ str(SL) +"\n"
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
  #print type(CreateQ())
  while True:
      Q()

if __name__ == '__main__':
    main()
