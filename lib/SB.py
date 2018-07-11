#!/usr/bin/python
# SysBackup module
# Version 0.4.6
import ConfigParser
import os

Pathini = "/etc/sbd/sbd.ini"

config = ConfigParser.ConfigParser()
config.read(Pathini)
global NameCluster
global Node
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
global pid
pid = str(os.getpid())


NameCluster = config.get('Main', 'NameCluster')
Node = config.get('Main', 'Node')
Connect = config.get('Main', 'MongoConnect')
DBs = config.get('Main',  'DBs')
AuthMechanism = config.get('Main',  'AuthMechanism')
DBUser = config.get('Main',  'DBUser')
DBUserPass = config.get('Main',  'DBUserPass')
Servers = "servers"
Cluster = "cluster"
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

t_skip_clean="Cleaning backup files has been skipped:"

def MongoCon():
    from pymongo import MongoClient
    from urllib import quote_plus
    global cl, coll, collCluster
    cl = MongoClient("mongodb://"+DBUser+":"
                     +DBUserPass+"@"+Connect+"/"
                     +DBs+"?authMechanism="+AuthMechanism)
    coll = cl[DBs][Servers]
    collCluster = cl[DBs][Cluster]






