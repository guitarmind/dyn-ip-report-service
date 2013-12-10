#!/bin/sh

# Get hostname
HOST_NAME=$(cat /etc/hostname)
echo 'HOST_NAME='$HOST_NAME

#Get IP address
IP_ADDR=$(ifconfig $1 | grep 'inet addr:' | cut -d: -f2 | cut -d' ' -f1)
echo 'IP_ADDR='$IP_ADDR

python report-client.py -a "http://localhost:1666/report" -s "$HOST_NAME" -i "$IP_ADDR" -p 22 > output.log &

exit 0;

