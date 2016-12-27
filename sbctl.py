#!/usr/bin/python
import sys
sys.path.insert(0, "lib")
import  SB


def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(SB.MongoConnect)
    coll = cl[SB.DBs][SB.Collection]

def MongoIn(Name,ServerIP,ServerPort,RsyncOpt,Priv,Dirs,DirsExclude):
    MongoCon()
    data = [{ "Name" :  Name ,  "ServerIP" : ServerIP,  "ServerPort" : ServerPort,  "RsyncOpt" : RsyncOpt , "Priv":Priv,   "Dirs" : Dirs,   "DirsExclude" :   DirsExclude,  "DateStart": "",  "DateEnd": ""  } ]
    coll.insert( data, True)

def List(allservers):   
    from colorama import Fore, Back, Style
    count=0
    for R in allservers:
        count=count+1
        global ServerName; ServerName=R['Name']
        global ServerIP; ServerIP=R['ServerIP']
        global ServerPort;ServerPort=R['ServerPort']
        global Priv; Priv=R['Priv']
        global RsyncOpt; RsyncOpt=R['RsyncOpt']
        global Dirs;Dirs=R['Dirs']
        global DirsExclude;DirsExclude=R['DirsExclude']
        global id;id=R['_id']
        print "##########################\n"
        print   (Fore.YELLOW + "Server name: "+ R['Name']  )
        print   "Server IP: ",  R['ServerIP']
        print(Style.RESET_ALL)
        print  "Server port: ",  R['ServerPort']
        print   "Priority: ",  R['Priv']
        print  "Options of rsync: "+ R['RsyncOpt']
        if R['DateStart']:
             print   "Last date of started backup: " + R['DateStart']
        if R['DateEnd']:
            print   "Last date of end backup: "  + R['DateEnd']
        print    "Dirs of backup example[/home/,/var ] " + R['Dirs']
        print    "Dirs exclude example[/home/Downloads/*,/var/log/*]: " + R['DirsExclude'] + "\n"
    print "##########################    amount of servers ", count
        


def MongoList():
    MongoCon()
    allservers = list(coll.find())
    List(allservers)

 
def MongoFind(Name):
    MongoCon()
    allservers = list(coll.find({ "Name": {'$regex': Name}}))
    List(allservers)
    
def PrCheck(Name, ServerIP, ServerPort, RsyncOpt, Priv, Dirs, DirsExclude):
    print "Check information\n Name: "+ Name +"\n Server IP: ",  ServerIP ,"\n Server SSH port: ",  ServerPort  ,""" 
    Rsync options: """+  RsyncOpt + "\nPriority: ",  Priv ,"\nDirectory :" + Dirs + "\nExclude directory :" + DirsExclude  

def MongoChange(Name):
    MongoCon()
    allservers = list(coll.find({ "Name": Name}))
    List(allservers)
    
    ServerNameN = raw_input('Enter name of server or client  [default:'+  ServerName +']: ') or ServerName
    ServerIPN= raw_input('Enter server IP [defaul:'+ ServerIP +'] : ') or  ServerIP
    ServerPortN= raw_input('Enter server SSH port [default: '+  str(ServerPort)  +' ] : ') or ServerPort
    RsyncOptN= raw_input('Enter options of rsync [default:'+ RsyncOpt +'] ') or RsyncOpt
    PrivN=raw_input('Priority  now [ '+ str(Priv)  +' ] : ') or Priv
    DirsN=raw_input('Dirs of backup now [ ' + Dirs + ' ] : ') or Dirs
    DirsExcludeN=raw_input('Dirs exclude now [ ' + DirsExclude + '] : ') or DirsExclude
    PrCheck(ServerNameN,ServerIPN,ServerPortN, RsyncOptN,PrivN,DirsN, DirsExcludeN )
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    choice = raw_input('Data are correct? ').lower()
    if choice in yes:
        #print id
        data = { "Name" :  ServerNameN ,  "ServerIP" : ServerIPN,  "ServerPort" : ServerPortN, "RsyncOpt" : RsyncOptN,  "Dirs" : DirsN, "DirsExclude" : DirsExcludeN,  "Priv" : PrivN    }
        #coll.update({'_id': R['_id']}, data, True)
        coll.update({'_id':id}, {"$set": data}, upsert=False)
        #coll.update({'Name': Name }, data})
        #db.servers.update({ "_id" : ObjectId("58533139399923269b261261")}, {$set: { "Name" : "Agnejka"  }}  )

    elif choice in no:
        print "Bye"
        exit (0)
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")

    
def add():
    ServerName = raw_input('Enter name of server or client: ')
    ServerIP = raw_input('Enter server IP: ')
    ServerPort = raw_input('Enter server SSH port [default:22] ') or 22
    RsyncOpt = raw_input('Enter options of rsync [default:-av] ') or '-av'
    Priv=raw_input('Priority default [ 20 ] : ') or 20
    Dirs=raw_input('Dirs of backup example[/root/,/var ] : ') or '/root/,/var'
    DirsExclude=raw_input('Dirs exclude example[/var/lib/*,/var/log/*] :') or '/var/lib/*,/var/log/*'
    PrCheck(ServerName,ServerIP,ServerPort, RsyncOpt,Priv,Dirs, DirsExclude )
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    choice = raw_input('Data are correct? ').lower()
    if choice in yes:
       MongoIn(ServerName,  ServerIP,  ServerPort,  RsyncOpt, Priv,  Dirs,  DirsExclude )
    elif choice in no:
        print "Bye"
        exit (0)
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")
 
 
def help():
    print "Help function: Basic Usage:\n "
    print "\t\taddhost - Add host to backup"
    print "\t\tlist    - List all hosts"
    print "\t\tsearch  - Search host name, example: search w1.host.com"
    print  "\t\tupdate  - Update data of host, example: update w1.host.com"
    print "\n"

def main():
    try:
        if sys.argv[1] == 'addhost':
            add()
        elif sys.argv[1] == 'list':
            MongoList()
        elif sys.argv[1] == 'search':
            MongoFind(sys.argv[2])
        elif sys.argv[1] == 'update':
            MongoChange(sys.argv[2])
        else:
            help()
    except IndexError:
        help()


if __name__ == '__main__': 
    main()
