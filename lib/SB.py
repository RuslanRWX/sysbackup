#!/usr/bin/python
import ConfigParser,  os

Pathini="sbd.ini"


config = ConfigParser.ConfigParser()
config.read(Pathini)
global MongoConnect
global DBs
global Collection
global Num_thread
global DirBackup
MongoConnect = config.get('Main', 'MongoConnect')
DBs = config.get('Main',  'DBs')
Collection = config.get('Main', 'Collection')
Num_thread = int(config.get('Main',  'Num_thread'))
DirBackup = config.get('Main', 'DirBackup')

