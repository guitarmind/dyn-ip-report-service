Dynamic IP Report Service
=========================

An utility service for automatical gathering of dynamic IP addresses on multiple hosts and VM guests.

![alt tag](https://raw.github.com/guitarmind/dyn-ip-report-service/master/snapshot.png)

In real-world scenarios, sometimes we encounter problems in managing large amount of physical hosts or virtual machines with dynamic IP addresses. It is really painful to update their address and status information manually. 

This service can greatly help the administrators who have similar management issues. 

The report client retrieves the latest information of current machine (e.g., hostname, IP address and SSH port) and sends to the report server. Report server maintains and summarizes a list of machine infomation for multiple host and VM guests. It also provides a summary page for administrators to see a full info list of all managed machines. Gmail alarm is supported by setting the alarm threshold.


###Installation on Ubuntu 12.04 LTS

For both client and server, make sure to install python and tornado library.

Python Requirement

    version >= 2.7

Install tornado by apt-get.

    sudo apt-get install python-tornado

###How to start Report Server

Start report-server by:

    python report-server.py 

Type the following command to check the options.

    python report-server.py --help
    
    Usage: report-server.py [options]

    Options:
      -h, --help            show this help message and exit
      -p PORT, --port=PORT  the listening port of dynamic IP report service
                            (default: 1666)
      -a ALARMTHRESHOLD, --alarm-threshold=ALARMTHRESHOLD
                            The threshold minutes to send alarm email by Gmail if the time passed since last update time is longer than it (default: 30)
      -g GMAILADDR, --gmail-addr=GMAILADDR
                            The administrator's Gmail
      -u USERNAME, --username=USERNAME
                            The administrator's Gmail username
      -s PASSWORD, --password=PASSWORD
                            The administrator's Gmail password
                            
The default listening port is **1666**. Change it to yours on startup.
Please make sure that the firewall is opened for lisenting port.

For example, you can change the port to 8080 by:

    python report-server.py -p 8080
    
To start it as a persistent service even after terminal logout:

    sudo nohup python report-server.py -p 8080 &

If you would like to enable alarm feature with Gmail, you need to configure settings:

    sudo nohup python report-server.py -a 60 -g "markpeng.ntu@gmail.com" -u "markpeng.ntu" -s "123456" &

The above setting triggers the function to send alarm email if there is any machine where the time passed since its last update time is longer than alarm threshold.

###How to start Report Client

Type the following command to check the options.

    python report-client.py --help
    
    Usage: report-client.py [options]
    
    Options:
      -h, --help            show this help message and exit
      -a APIURL, --api-url=APIURL
                            the URL of Dynamic Report IP Service.
      -s HOSTNAME, --hostname=HOSTNAME
                            the hostname of current machine.
      -i IP, --ip=IP        the IP address of current machine.
      -p SSHPORT, --ssh-port=SSHPORT
                            the SSH port of current machine.
      -m MODE, --mode=MODE  two options: once | period
      -n NIC, --nic=NIC     the target NIC to report IP address.
      -t TIME, --time=TIME  the time interval in minutes for periodical tasks.


For instance:

    python report-client.py -a "http://localhost:1666/report" -m "period" -n "eth0" -t 10


Similarly, to start it as a persistent service even after terminal logout:

    sudo nohup report-client.py -a "http://localhost:1666/report" -m "period" -n "eth0" -t 10 &

###How to access Summary Page

You can access the summary page under the '**/summary**' path of current domain.
For instance, if you setup report server on localhost at port 1666, then the link for summary page would be:

    http://localhost:1666/summary


##Changelog

####0.0.1 - 2013-12-10

Features:

  - Client/Server architecture for reporting service
  - JSON-based communications
  - Support timer for gathering client machine info periodically
  - Provides a summary page for administrator

####0.0.2 - 2013-12-22

Features:

  - Support machine alarms by Gmail


##Copyright and License

Author: Mark Peng (markpeng.ntu at gmail)

All codes are under the [Apache 2.0 license](LICENSE).
