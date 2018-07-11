#!/bin/sh 

IP=`ip addr | grep -v -w "lo" | grep -Eo 'inet [0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}' | awk '{ print $2 }' | head -1`
host=$(hostname)

read -p "	|->  Your Server IP: default [ "$IP" ]: " ServIP
 : ${ServIP:=$IP}

read -p "	|->  You cluster name: default [ sysbackup cluster ]: " cluster
 : ${cluster:="sysbackup cluster"}

read -p "	|->  You node name: default [ "$host" ]: " node
 : ${node:=$host}


echo "Start install Server backup "
if [ ! -d /etc/sbd ]; then { mkdir -p /etc/sbd;  } fi 

cp sbd.ini /etc/sbd/

echo "Install sbd"
cp dist/sbd /usr/sbin/sbd
cp lib/SB.py /usr/lib/python2.7/

echo "install sbctl" 
cp dist/sbctl /usr/sbin/sbctl


echo "create systemd unit"
cp sbd.service /etc/systemd/system/
systemctl daemon-reload

cp sbd.logrotate  /etc/logrotate.d/
if [ ! -d /usr/share/sbcl ]; then { mkdir -p /usr/share/sbcl; } fi 
cp dist/sbcl /usr/share/sbcl/
cp sbcl.ini /usr/share/sbcl/
sed -i "s/127\.0\.0\.1/$ServIP/" /usr/share/sbcl/sbcl
sed -i "s/127\.0\.0\.1/$ServIP/" /usr/share/sbcl/sbcl.ini
sed -i "s/127\.0\.0\.1/$ServIP/" /etc/sbd/sbd.ini
sed -i "s/yourcluster/$cluster/" /etc/sbd/sbd.ini
sed -i "s/hostname/$host/" /etc/sbd/sbd.ini


echo "ServerBackup has been installed. You can start and stop by using systemd; systemctl status sbd "
echo "Configuration file: /etc/sbd/sbd.ini"
echo "Your configuration parameters"
mkdir /var/log/sbd
cat /etc/sbd/sbd.ini
