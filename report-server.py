#!/usr/bin/env python
import tornado.httpserver
import tornado.ioloop
import tornado.web
import optparse
import logging
import traceback
import os
from os import listdir
from os.path import isfile, join
import json

"""
Logging settings
"""
logger = logging.getLogger('DynIPReport')
logger.setLevel(logging.INFO)
try:
    os.remove('dyn_report_service.log')
except OSError:
    pass
fileHandler = logging.FileHandler('dyn_report_service.log')
fileHandler.setLevel(logging.INFO)
# console handler
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
fileHandler.setFormatter(formatter)
consoleHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)

# global variables
workingFolderPath = os.getcwd()

"""
Handles the report of IP address from client.
"""
class DynIpReportHanlder(tornado.web.RequestHandler):
    def post(self):
        try:
            self.set_header("Content-Type", "application/json; charset=UTF-8")

            # parse received json
            jsonobj = json.loads(self.request.body)

            hostname = jsonobj['hostname']
            ip = jsonobj['ip']
            ssh_port = jsonobj['ssh_port']
            update_time = jsonobj['update_time']

            print "Received report: " + hostname + ", " + ip + ", " + ssh_port + ", " + update_time

            # create temp folder if not exits
            tmpFileFolder = workingFolderPath + "/temp"
            if not os.path.exists(tmpFileFolder):
                os.makedirs(tmpFileFolder)

            # write to text file
            f = open(tmpFileFolder + "/" + hostname + ".txt", "w")
            try:
                f.write(ip + ',' + ssh_port + ',' + update_time + '\n')
            finally:
                f.close()

            # send response json
            response = { 'result': 'OK' }
            self.write(response)

            print response

        except:
            tb = traceback.format_exc()
            errMsg = { 'error': tb }
            self.write(errMsg)
            logger.error(tb)

"""
Handles the summary data for adminstrator.
"""
class SummaryDataHanlder(tornado.web.RequestHandler):
    def get(self):
        try:
            self.set_header("Content-Type", "text/html; charset=UTF-8")

            responseData = []
            # read from text file
            tmpFileFolder = workingFolderPath + "/temp"
            os.chdir(tmpFileFolder)
            filePathList = os.listdir(".")
            filePathList.sort()
            os.chdir(workingFolderPath)

            for fileFullName in filePathList:
                rowData = None
                fileName = fileFullName.replace(".txt", "")
                f = open(tmpFileFolder + "/" + fileFullName, "r")
                try:
                    # Read the entire contents of a file at once.
                    raw = f.read()
                    if raw is not None:
                        data = raw.split(',')
                        rowData = { 'hostname': fileName, 'ip': data[0], 'ssh_port': data[1], 'update_time': data[2] }
                        responseData.append(rowData)
                finally:
                    f.close()

            responseMsg = { 'result': responseData }

            self.write(responseMsg)

        except IOError:
            tb = traceback.format_exc()
            errMsg = { 'error': tb }
            self.write(errMsg)
            logger.error(tb)
        except:
            tb = traceback.format_exc()
            errMsg = { 'error': tb }
            self.write(errMsg)
            logger.error(tb)

"""
Handles the summary page for adminstrator.
"""
class SummaryPageHanlder(tornado.web.RequestHandler):
    def get(self):
        try:
            self.set_header("Content-Type", "text/html; charset=UTF-8")

            with open(os.path.join(workingFolderPath, 'website/index.html')) as f:
                self.write(f.read())

        except IOError:
            tb = traceback.format_exc()
            errMsg = { 'error': tb }
            self.write(errMsg)
            logger.error(tb)
        except:
            tb = traceback.format_exc()
            errMsg = { 'error': tb }
            self.write(errMsg)
            logger.error(tb)

def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--port', dest='port', help='the listening port of dynamic IP report service (default: 1666)')
    (options, args) = parser.parse_args()

    port = options.port
    if not options.port:   # if port is not given, use the default one 
      port = 1666
   
    application = tornado.web.Application([
                    (r"/report", DynIpReportHanlder),
                    (r"/data", SummaryDataHanlder),
                    (r"/summary", SummaryPageHanlder),
                    (r'/css/(.*)',tornado.web.StaticFileHandler,{'path':"website/css"}),
                    (r'/js/(.*)',tornado.web.StaticFileHandler,{'path':"website/js"})])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    print "Dynamic IP Report Service starts at port " + str(port) + "."
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

