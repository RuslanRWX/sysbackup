#!/bin/sh 

IP=`ip addr | grep -v -w "lo" | grep -Eo 'inet [0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}' | awk '{ print $2 }' | head -1`

#read -p "	|->  Your Server IP: default [ "$IP" ]: " ServIP
# : ${ServIP:=$IP}

#sed -i "s/127\.0\.0\.1/$ServIP/" sbcl.py
#sed -i "s/127\.0\.0\.1/$ServIP/" sbd.ini

echo "Start install Server backup "
mkdir /etc/sbd
cp sbd.ini /etc/sbd/

echo "Install sbd"
cp sbd /usr/sbin/
cp lib/* /usr/lib/python2.7/

echo "install sbctl" 
cp sbctl /usr/sbin/


echo "create systemd unit"
cp sbd.service /etc/systemd/system/
systemctl daemon-reload

cp sbd.logrotate  /etc/logrotate.d/
mkdir /usr/share/sbcl/
cp sbcl.py /usr/share/sbcl/



echo "ServerBackup has been installed\n You can start and stop by using sysyemd; systemctl status sbd "
echo "Configuration file is /etc/sbd/sbd.ini"
