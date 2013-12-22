#!/bin/sh

cd /home/uitox/dyn-ip-report-service
sudo nohup python report-server.py -a 30 -g "mark.peng@uitox.com" -u "mark.peng@uitox.com" -s "Uitox\\!\\!\\)\\$" &

