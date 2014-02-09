#!/bin/sh

cd /home/uitox/dyn-ip-report-service
sudo nohup python report-server.py -a 30 -g "xxxx" -u "xxxx" -s "xxx" -r "xxxx"  &

