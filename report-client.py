#!/usr/bin/env python
import sys
import optparse
import tornado.httpclient
import simplejson, json
import datetime
import subprocess
import functools

# global variable
periodMode = None
intervalTime = 30 * 1000

"""
Send machine info to report server once.
"""
def reportToServer(apiUrl, hostname, ip, sshPort):
    update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    request = { 'hostname': hostname, 'ip': ip, 'ssh_port': sshPort, 'update_time': update_time }
    post_data = json.dumps(request)

    headers = { 'Content-Type': 'application/json; charset=UTF-8' }
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_client.fetch(apiUrl, handle_request, method='POST', headers=headers, body=post_data)
    print "Sending request: " + post_data
    tornado.ioloop.IOLoop.instance().start()

"""
Send machine info to report server periodically.
"""
def periodReportToServer(apiUrl, nic):
    # Start period timer
    loop = tornado.ioloop.IOLoop.instance()
    scheduler = tornado.ioloop.PeriodicCallback(functools.partial(sendNewReport, apiUrl=apiUrl, nic=nic), intervalTime, io_loop=loop)

    print "Starting period timer ... (interval: " + str(intervalTime) + " milliseconds)"
    scheduler.start()
    loop.start()

"""
Send machine info using data gathered from shell command.
"""
def sendNewReport(apiUrl, nic):
    update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # print "update_time: " + update_time

    # get hostname info
    p = subprocess.Popen(['cat', '/etc/hostname'], stdout=subprocess.PIPE)
    (hostname, err) = p.communicate()
    hostname = hostname.replace('\n', '')
    # print "hostname: " + hostname

    # get IP address info
    p = subprocess.Popen(['ifconfig', nic], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'inet addr:'], stdin=p.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['cut', '-d:', '-f2'], stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen(['cut', '-d', ' ', '-f1'], stdin=p3.stdout, stdout=subprocess.PIPE)
    (ip, err) = p4.communicate()
    ip = ip.replace('\n', '')
    # print "ip: " + ip

    # get SSH port info
    try:
        p = subprocess.Popen(['cat', '/etc/ssh/sshd_config'], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', 'Port'], stdin=p.stdout, stdout=subprocess.PIPE)
        p3 = subprocess.Popen(['awk', '{ print $2 }'], stdin=p2.stdout, stdout=subprocess.PIPE)
        (sshPort, err) = p3.communicate()
        sshPort = sshPort.replace('\n', '')
    except:
        sshPort = "22"
    # print "sshPort: " + sshPort

    request = { 'hostname': hostname, 'ip': ip, 'ssh_port': sshPort, 'update_time': update_time }
    post_data = json.dumps(request)

    headers = { 'Content-Type': 'application/json; charset=UTF-8' }
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_client.fetch(apiUrl, handle_request, method = 'POST', headers = headers, body = post_data)
    print "Sending request: " + post_data

def handle_request(response):
    if response.error:
        print "Error: ", response.error
    else:
        print "Got response: " + response.body

    if periodMode == "once":
        tornado.ioloop.IOLoop.instance().stop()

def main():
    parser = optparse.OptionParser()
    parser.add_option('-a', '--api-url', dest='apiUrl', help='the URL of Dynamic Report IP Service.')
    parser.add_option('-s', '--hostname', dest='hostname', help='the hostname of current machine.')
    parser.add_option('-i', '--ip', dest='ip', help='the IP address of current machine.')
    parser.add_option('-p', '--ssh-port', dest='sshPort', help='the SSH port of current machine.')
    parser.add_option('-m', '--mode', dest='mode', help='two options: once | period')
    parser.add_option('-n', '--nic', dest='nic', help='the target NIC to report IP address.')
    parser.add_option('-t', '--time', dest='time', help='the time interval in minutes for periodical tasks.')
    (options, args) = parser.parse_args()

    global periodMode

    if not options.mode:
        periodMode = "once"
    else:
        periodMode = options.mode

    if not options.apiUrl:   # if apiUrl is not given
        parser.error('api-url not given')

    if periodMode != "period":
        if not options.hostname:   # if hostname is not given
            parser.error('hostname not given')
        if not options.ip:   # if ip is not given
            parser.error('ip not given')
        if not options.sshPort:   # sshPort ip is not given
            parser.error('sshPort not given')
    else:
        if not options.nic:   # if nic is not given
            parser.error('nic not given')
        if not options.time:   # if time is not given
            parser.error('time not given')
        else:
            global intervalTime
            intervalTime = float(options.time) * 60 * 1000

    # call report API
    if periodMode != "period":
        reportToServer(options.apiUrl, options.hostname, options.ip, options.sshPort)
    else:
        periodReportToServer(options.apiUrl, options.nic)
 
if __name__ == '__main__':
    main()
