#Deploy the ServerBackup

Inatall mongodb on Debian/Ubunut

apt-get install mongodb

Install pip on Debian/Ubunut

apt-get install python-pip

Install git 

apt-get install git

git clone

git clone https://github.com/ruslansvs2/ServerBackup.git

Install python  module pymongo

pip install pymongo

Install python module colorama

pip install colorama

Install sbd and sbctl 
./install.sh


vim /etc/logrotate.d/sbd and add:<br>
/var/log/sbd/*.log {<br>
  rotate 10 <br>
  daily <br>
  compress <br>
  missingok <br>
  notifempty <br>
}

 
