Dynamic IP Report Service
=========================

A utility service for automatically gathering of dynamic IP addresses on multiple hosts and VM guests.

In real-world scenarios, sometimes we encounter problems in managing large amount of physical hosts or virtual machines with dynamic IP addresses. It is really painful to update their address information manually. 

This service can greatly help the administrators who have similar management issues. 

The report client retrieves the latest information of current machine (e.g., hostname, IP address and SSH port) and sends to the report server. Report server maintains and summarizes a list of machine infomation for multiple host and VM guests. It also provides a summary page for administrators to see a full info list of all managed machines.


###Installation on Ubuntu 12.04 LTS

For both client and server, make sure to install python and tornado library.

Python Requirement

    version >= 2.7

Install tornado by apt-get.

    sudo apt-get install python-tornado




##Changelog

####0.0.1 - 2013-12-10

Features:

  - Client/Server architecture for reporting service
  - Support timer for reporting client info periodically
  - Provides a summary page for administrator



##Copyright and License

Author: Mark Peng (markpeng.ntu at gmail)

All codes are under the [Apache 2.0 license](LICENSE).
