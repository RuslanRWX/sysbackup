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
apt install mongodb
apt install git -y
```  
  
If you didn’t get any errors your server ready to install sysbackup

```
git clone https://github.com/ruslansvs2/sysbackup.git
cd sysbackup
./install.sh  
```

