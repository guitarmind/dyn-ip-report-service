#!/usr/bin/env python
import sys
import optparse
import tornado.httpclient
import simplejson, json
import datetime

"""
Get result string from tesseract API
"""
def reportToServer(apiUrl, hostname, ip, sshPort):
    update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    request = { 'hostname': hostname, 'ip': ip, 'ssh_port': sshPort, 'update_time': update_time }
    post_data = json.dumps(request)

    headers = { 'Content-Type': 'application/json; charset=UTF-8' }
    http_client = tornado.httpclient.AsyncHTTPClient()
    http_client.fetch(apiUrl, handle_request, method = 'POST', headers = headers, body = post_data)
    print "Sending request: " + post_data
    tornado.ioloop.IOLoop.instance().start()

def handle_request(response):
    if response.error:
        print "Error: ", response.error
    else:
        print "Got response: " + response.body
    tornado.ioloop.IOLoop.instance().stop()

def main():
    parser = optparse.OptionParser()
    parser.add_option('-a', '--api-url', dest='apiUrl', help='the URL of Dynamic Report IP Service.')
    parser.add_option('-s', '--hostname', dest='hostname', help='the hostname of current machine.')
    parser.add_option('-i', '--ip', dest='ip', help='the IP address of current machine.')
    parser.add_option('-p', '--ssh-port', dest='sshPort', help='the SSH port of current machine.')
    (options, args) = parser.parse_args()

    if not options.apiUrl:   # if apiUrl is not given
        parser.error('api-url not given')
    if not options.hostname:   # if hostname is not given
        parser.error('hostname-url not given')
    if not options.ip:   # if ip is not given
        parser.error('ip not given')
    if not options.sshPort:   # sshPort ip is not given
        parser.error('sshPort not given')

    # call report API
    reportToServer(options.apiUrl, options.hostname, options.ip, options.sshPort)
 
if __name__ == '__main__':
    main()
