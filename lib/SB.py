#!/usr/bin/env python
import ConfigParser,  os

Pathini=os.path.dirname(__file__), 'sbd.ini'

config = ConfigParser.ConfigParser()
config.read(Pathini)
global MongoConnect
global DBs
global Collection
global Num_thread
global DirBackup
global Pidfile
MongoConnect = config.get('Main', 'MongoConnect')
DBs = config.get('Main',  'DBs')
Collection = config.get('Main', 'Collection')
Num_thread = int(config.get('Main',  'Num_thread'))
DirBackup = config.get('Main', 'DirBackup')
Pidfile = config.get('Main', 'Pidfile')

def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(MongoConnect)
    coll = cl[DBs][Collection]
