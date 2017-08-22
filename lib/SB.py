#!/usr/bin/python
# SysBackup module
# Version 0.4.0
import ConfigParser

Pathini = "/etc/sbd/sbd.ini"

config = ConfigParser.ConfigParser()
config.read(Pathini)
global MongoConnect
global DBs
global Collection
global DBUser
global DBUserPass
global Num_thread
global DirBackup
global Pidfile
global Log
global LogError
global LogDirListen
global IP
global Port
global TimeCheck
global PublickKey

MongoConnect = config.get('Main', 'MongoConnect')
DBs = config.get('Main',  'DBs')
DBUser = config.get('Main',  'DBUser')
DBUserPass = config.get('Main',  'DBUserPass')
CollectionMain = "servers"
Num_thread = int(config.get('Main',  'Num_thread'))
DirBackup = config.get('Main', 'DirBackup')
Pidfile = config.get('Main', 'Pidfile')
tmp = config.get('Main', 'tmp')
Log = config.get('Main', 'Log')
LogError = config.get('Main', 'LogError')
LogDir = config.get('Main', 'LogDir')
IP = config.get('Main', 'ListenIP')
Port = config.get('Main', 'ListenPort')
TimeCheck = int(config.get('Main', 'TimeCheck'))
PublickKey = config.get('Main', 'PublickKey')


def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient("mongodb://"+DBUser+":"+DBUserPass+"@"+MongoConnect)
    coll = cl[DBs][CollectionMain]


