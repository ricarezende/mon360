##### InfluxDB Server Configuration
1 - Update the package manager
[root] # yum update

2 - Install Python 3
[root] # yum install -y python3

3 - Install needed libraries
[root]# yum install gcc python3-devel.x86_64 python3-pip
[root]# pip3 install psutil
[root]# pip3 install cx_Oracle
[root]# pip3 install pyinputplus
[root]# pip3 install paramiko scp

4 - Install InfluxDB on your server

5 - Clone mon360 Git Repository
???????

6 - Run mon360 in server mode with -config option
[user]$ cd ~/mon360
[user]$ ./mon360.py -server -config


##### InfluxDB Client Configuration
1 - Update the package manager
[root] # yum update

2 - Install Python 3
[root] # yum install -y python3

3 - Install needed libraries
[root]# yum install gcc python3-devel.x86_64 python3-pip
[root]# pip3 install psutil
[root]# pip3 install cx_Oracle
[root]# pip3 install pyinputplus
[root]# pip3 install paramiko scp

4 - Configure Environment
[user]$ ./mon360.py -config
