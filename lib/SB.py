#!/usr/bin/python
# Version 0.2.2
import ConfigParser,  os

Pathini="/etc/sbd/sbd.ini"

config = ConfigParser.ConfigParser()
config.read(Pathini)
global MongoConnect
global DBs
global Collection
global Num_thread
global DirBackup
global Pidfile
global Log
global LogDir
MongoConnect = config.get('Main', 'MongoConnect')
DBs = config.get('Main',  'DBs')
Collection = config.get('Main', 'Collection')
Num_thread = int(config.get('Main',  'Num_thread'))
DirBackup = config.get('Main', 'DirBackup')
Pidfile = config.get('Main', 'Pidfile')
tmp = config.get('Main', 'tmp')
Log = config.get('Main', 'Log')
LogDir = config.get('Main',  'LogDir')
def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(MongoConnect)
    coll = cl[DBs][Collection]
