#!/usr/bin/python
# Version 0.2.3
import ConfigParser

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
global LogDirListen
global IP
global Port
MongoConnect = config.get('Main', 'MongoConnect')
DBs = config.get('Main',  'DBs')
Collection = config.get('Main', 'Collection')
Num_thread = int(config.get('Main',  'Num_thread'))
DirBackup = config.get('Main', 'DirBackup')
Pidfile = config.get('Main', 'Pidfile')
tmp = config.get('Main', 'tmp')
Log = config.get('Main', 'Log')
LogDir = config.get('Main',  'LogDir')
IP = config.get('Main',  'ListenIP')
Port = config.get('Main',  'ListenPort')


def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(MongoConnect)
    coll = cl[DBs][Collection]
