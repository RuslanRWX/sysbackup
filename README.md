# Sysbackup
Sysbackup - is a free backup software with clusterization capabilities. 


If you have a bunch of servers it can be useful to use Sysbackup.
This software allows you keep backup files in different places and makes it easy to manage backup strategies.

#### Benefits:
* Clusterizations 
* Multi-backup, thread 
* Security
* Managing all your backups from different places
* Backup hosts don’t have access to the server
* Manage frequency of backups
* Multiple copies of backups 


### Architecture

*Sysbackup* is a cluster backup software based on rsync. 

Terminologies:<br/>
*Backup server* or *node* is a server-executed backup. It has backup storage and installed Sysbackup software.<br/>
*Hosts* are servers which have to be backed up.<br/>
*Master database* is a MongoDB database which stores backup logic.<br/>
*sbd* is a daemon for backing the host up<br/>
*sbctl* is a CLI for configuring sbd, logic and  behaviour.<br/>
*sbc* is a client on a host server, required only for backing up the MySQL database and managing this server. *sbc* can also configure its own backup logic. It can be useful in case you don’t want to go to the backup server to make some changes.<br/>
 
*Sysbackup* is configured by using its own client program *sbctl* 

#### Minimal architecture 
Minimal architecture requires one a backup daemon (*sysbackup*) and master database (*MongoDB*), plus one or more host servers which need to be backed up.
 

#### Cluster architecture 
Cluster architecture requires two or more backup servers and a bunch of host servers.
In this case, daemons (*sysbackup*) have access to the same databases.



### Step 1: Installation 
Install on Debian/Ubuntu<br/>
To install the dependencies just execute the commands below: 

```
apt update
apt install mongodb -y
apt install git -y
```  
  
If you didn’t get any errors your server ready to install sysbackup

```
git clone https://github.com/ruslansvs2/sysbackup.git
cd sysbackup
./install.sh  
```

The output should look like this:
```
	|->  Your server IP: default [ 192.168.1.2 ]:                    - you can change your IP address
	|->  You cluster name: default [ sysbackup cluster ]: test       - you can change your cluster name
	|->  You node name: default [ test.host.org ]:                   - name of your backup server 

Start installing the server backup 
Install sbd
install sbctl
create systemd unit

Sysbackup has been installed. You can start and stop by using systemd; systemctl status sbd
Configuration file: /etc/sbd/sbd.ini
Your configuration parameters
[Main]
# Backup cluster name
NameCluster: sysbackup cluster
# Name node
Node: zabbix.kloomba.ua
# Mongo connect
MongoConnect: localhost:27017
# Mongo database
DBs: sysbackup
# security authorization
# If your MongoDB is started with access control you have to set the next three parameters
# AuthMechanism, DBUser and DBUserPass.
# authorization mechanism ( for MongoDB 3.0 or later )
# SCRAM-SHA-1 is the default authentication mechanism for authentication with MongoDB 3.0 or later.
# Before MongoDB 3.0 the default authentication mechanism was MONGODB-CR.
# If your MongoDB is using another authentication mechanism you have to use the corresponding method.
AuthMechanism: MONGODB-CR
# Mongo user 
DBUser: sysbackup
# Mongo user's password
DBUserPass: mypass
# Number of threads of backup
Num_thread: 2
# Backup directory on server
DirBackup: /var/backup
# Pid file
Pidfile: /var/run/sbd.pid
# tmp directory 
tmp: /tmp/sbd
# Log directory 
LogDir: /var/log/sbd
# Log file
Log: /var/log/sbd/sbd.log
# Error log file
LogError: /var/log/sbd/sbd.error.log
# Listen IP address and port
ListenIP: 185.151.247.112
ListenPort: 29029
# Timeout
TimeCheck: 3600
# Public key 
PublicKey: /root/.ssh/id_rsa.pub

```
Sysbackup has been installed  

### Step 2: Configuration 

Backup server has configuration file placed in /etc/sbd/sbd.ini; we have to configure it before using it. 

#### Configuring MongoDB 

For more security you have to use authentication; for more information you can refer to the official documentation.  https://docs.mongodb.com/manual/tutorial/enable-authentication/.

Adding admin user and password for MongoDB:

```
# mongo
MongoDB shell version: 3.2.11
connecting to: test
> use admin
switched to db admin
> db.createUser(
... {
... user: "root",
... pwd: "test",
... roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
... }
... )

You should get this output:
Successfully added user: {
	"user" : "root",
	"roles" : [
		{
			"role" : "userAdminAnyDatabase",
			"db" : "admin"
		},
		"readWriteAnyDatabase"
	]
}
```

#### Configuring the MongoDB file:
By using the editor open the /etc/mongodb.conf file and change the following parameters:
Uncommit or add: 

*auth = true*

Change it if you want to use the cluster backup architecture 

*bind_ip = 127.0.0.1* to *bind_ip = 0.0.0.0* 

> NOTE: Don’t forget about firewall. Your firewall has to allow traffic to the 27017 port for your hosts and forbid for others.


Restart MongoDB by following this command:

```
systemctl restart mongodb.service
```

Add MongoDB user for our database
> Note: In our example we have installed MongoDB version 3.2 

Go to the MongoDB Shell by using the admin password

```
mongo  --port 27017  -u "root" -p  --authenticationDatabase "admin"

>  use sysbackup
switched to db sysbackup
> db.createUser(
...   {
...     user: "sysbackup",
...     pwd: "test",
...    roles: [ { role: "readWrite", db: "sysbackup" },
...             { role: "read", db: "reporting" } ]
...   }
... )
```

You should get this output:

```
Successfully added user: {
	"user" : "sysbackup",
	"roles" : [
		{
			"role" : "readWrite",
			"db" : "sysbackup"
		},
		{
			"role" : "read",
			"db" : "reporting"
		}
	]
}
```

#### Configuring Sysbackup daemon 

Using your favorite editor open the configuration file and edit it.
It my example I use vim

```
vim /etc/sbd/sbd.ini 
```
