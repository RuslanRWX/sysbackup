#!/usr/bin/python
# SySBackup deamon
# Copyright (c) 2017 Ruslan Variushkin,  ruslan@host4.biz
Version = "0.4.10"


import threading
import Queue
import sys
import time
import datetime
import os
#sys.path.append("lib/")
import SB
import daemon


def worker():
    while True:
        item = q.get()
        Back = daemon.backup(item)
        Back.run()
        q.task_done()


def Q():
    global q
    q = Queue.Queue(0)
    for i in range(SB.Num_thread):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    for item in daemon.create_queue():
        q.put(item["Name"])
    q.join()



def help():
    return """Help function: Basic Usage:\n
    \tversion    - show version
    \tstart      - Start the sbd deamon
    \tstop       - Stop the sbd deamon
    \trestart    - Restart the sbd deamon
    \tbackup     - Start backup just one node, example [sbd backup myhost] 
    \thelp       - Print help\n"""


def Stop():
    text = "\nStoped sbd {date}\n".format(date=datetime.datetime.now())
    daemon.log(text, SB.Log)
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
        SB.coll.update({"Status": "running"}, {"$set": DateUp}, upsert=False, multi=True)
        print "sbd is stopped"
    else:
        print "sbd is not running"


def Start():
    text = "\nStart sbd version:{ver}, date: {date}\nNode name:{node}\n".format(
        ver=Version, date=datetime.datetime.now(), node=SB.Node)
    daemon.log(text, SB.Log)
    print text
    t = threading.Thread(target=daemon.API)
    t.daemon = True
    t.start()
    while True:
        text = "\nStart queue, date: {date}".format(
            date=datetime.datetime.now())
        daemon.log(text, SB.Log)
        Q()
        text = "\nQueue is done, date: {date}\n".format(
            date=datetime.datetime.now())
        daemon.log(text, SB.Log)
        time.sleep(SB.TimeCheck)


def main():
    try:
        if sys.argv[1] == 'start':
            daemon.check()
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
            Back = daemon.backup(name, 1)
            try:
                Back.run()
            except:
                print "Error: have not host like " + sys.argv[2] + " !"
        elif sys.argv[1] == 'version':
            print Version
        else:
            print help()
    except IndexError:
        print help()


if __name__ == '__main__':
    main()
