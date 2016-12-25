#!/usr/bin/python
import sys
MongoConnect='localhost:27017'

def MongoCon():
    from pymongo import MongoClient
    global cl
    global coll
    cl = MongoClient(MongoConnect)
    coll = cl["ServersBackup"]["servers"]

def MongoIn(Name,  ServerIP,  ServerPort,  RsyncOpt):
    MongoCon()
    data = [{ "Name" :  Name ,  "ServerIP" : ServerIP,  "ServerPort" : ServerPort,  "RsyncOpt" : RsyncOpt } ]
    coll.insert( data, True)
    
def MongoList():
    MongoCon()
    allservers = list(coll.find())
    count=0
    for R in allservers:
        count=count+1
        print "##########################\n"
        print  "Server name: "+ R['Name']
        print  "Server IP: ",  R['ServerIP']
        print  "Server port: ",  R['ServerPort']
        print  "Options of rsync: "+ R['RsyncOpt'] +"\n"
    print "################\namount of servers ", count
    
def MongoFind(Name):
    MongoCon()
    allservers = list(coll.find({ "Name": {'$regex': Name}}))
    count=0
    for R in allservers:
        count=count+1
        print "##########################\n"
        print  "Server name: "+ R['Name']
        print  "Server IP: ",  R['ServerIP']
        print  "Server port: ",  R['ServerPort']
        print  "Options of rsync: "+ R['RsyncOpt'] +"\n"
    print "################\namount of servers ", count

def MongoChange(Name):
    MongoCon()
    allservers = list(coll.find({ "Name": Name}))
    count=0
    for R in allservers:
        count=count+1
        print "##########################\n"
        print  "Server name: "+ R['Name']
        print  "Server IP: ",  R['ServerIP']
        print  "Server port: ",  R['ServerPort']
        print  "Options of rsync: "+ R['RsyncOpt'] +"\n"
        Rport=R['ServerPort']
    Name = raw_input('Enter name of server or client  [defaul:'+  R['Name'] +']: ') or R['Name']
    ServerIP= raw_input('Enter server IP [defaul:'+ R['ServerIP'] +'] : ') or R['ServerIP']
    ServerPort= raw_input('Enter server SSH port [default: '+  str(R['ServerPort'])  +' ] : ') or R['ServerPort']
    RsyncOpt= raw_input('Enter options of rsync [default:'+ R['RsyncOpt'] +'] ') or R['RsyncOpt']
    print "Check information\n Name: "+ Name +"\n Server IP: ",  ServerIP ,"\n Server SSH port: ",  ServerPort  ,"\n Rsync options: "+  RsyncOpt
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    choice = raw_input('Data are correct? ').lower()
    if choice in yes:
        print R['_id']
        id=R['_id']
        data = { "Name" :  Name ,  "ServerIP" : ServerIP,  "ServerPort" : ServerPort,  "RsyncOpt" : RsyncOpt }
        #coll.update({'_id': R['_id']}, data, True)
        coll.update({'_id':id}, {"$set": data}, upsert=False)
        #coll.update({'Name': Name }, data})
        #db.servers.update({ "_id" : ObjectId("58533139399923269b261261")}, {$set: { "Name" : "Agnejka"  }}  )

    elif choice in no:
        print "Bye"
        exit (0)
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")

    
def ask():
    Name = raw_input('Enter name of server or client: ')
    ServerIP = raw_input('Enter server IP: ')
    ServerPort = raw_input('Enter server SSH port [default:22] ') or 22
    RsyncOpt = raw_input('Enter options of rsync [default:-av] ') or '-av'
    print "Check information\n Name: "+ Name +"\n Server IP: ",  ServerIP ,"\n Server SSH port: ",  ServerPort  ,"\n Rsync options: "+  RsyncOpt
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    choice = raw_input('Data are correct? ').lower()
    if choice in yes:
       MongoIn(Name,  ServerIP,  ServerPort,  RsyncOpt)
    elif choice in no:
        print "Bye"
        exit (0)
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")
 
 
def help():
     print "Ok"

def main():
    if sys.argv[1] == 'addhost':
        ask()
    elif sys.argv[1] == 'list':
        MongoList()
    elif sys.argv[1] == 'search':
        MongoFind(sys.argv[2])
    elif sys.argv[1] == 'update':
        MongoChange(sys.argv[2])
    else:
        help()


if __name__ == '__main__': 
    main()
