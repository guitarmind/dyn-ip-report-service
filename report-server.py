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
import datetime
import smtplib
from email.MIMEText import MIMEText

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
alarmThresholdInMinutes = 30
adminGmail = None
adminGmailUsername = None
adminGmailPassword = None
mailRecipients = []

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

            alarmMachines = []
            alarmLastUpdateTimes = []
            for fileFullName in filePathList:
                rowData = None
                fileName = fileFullName.replace(".txt", "")
                f = open(tmpFileFolder + "/" + fileFullName, "r")
                try:
                    # Read the entire contents of a file at once.
                    raw = f.read()
                    if raw is not None:
                        data = raw.replace('\n', '').split(',')
                        rowData = { 'hostname': fileName, 'ip': data[0], 'ssh_port': data[1], 'update_time': data[2] }
                        
                        # Send mail to administrator if last update time is longer than threshold
                        last_update_time = datetime.datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S')
                        timspan = datetime.datetime.now() - last_update_time
                        if timspan > datetime.timedelta(minutes=int(alarmThresholdInMinutes)):
                            rowData['alarm'] = True
                            alarmMachines.append(fileName)
                            alarmLastUpdateTimes.append(data[2])

                        responseData.append(rowData)
                finally:
                    f.close()


            if len(alarmMachines) > 0:
                machines = ', '.join(alarmMachines)
                # Specifying from and to addresses
                fromAddr = "dyn.reporter@gmail.com"
                toAddrs = mailRecipients
                toAddrs.append(adminGmail)
                subject = "Dynamic IP Report Service: Machine Alarm"
                content = """<strong>Alarm: </strong><br/>
                             Something wrong with the following machines: <br/>"""
                for index, machine in enumerate(alarmMachines):
                    updateTime = alarmLastUpdateTimes[index]
                    content += """<font color=\"red\" style=\"font-size:18px\">%(machine)s</font><br/>
                                 (last update time: %(updateTime)s)<br/><br/>""" % { 'machine': machine, 'updateTime': updateTime }
                content += """Please check their status.<br/><br/>
                              Sent by <strong>Dynamic IP Report Service</strong>
                           """
                msg = MIMEText(content, 'html')
                msg['Subject'] = subject
                msg['From'] = fromAddr
                msg['To'] = ', '.join(toAddrs)

                # Sending the mail
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.ehlo()
                server.starttls()
                print adminGmailUsername, adminGmailPassword
                server.login(adminGmailUsername, adminGmailPassword)
                server.sendmail(fromAddr, toAddrs, msg.as_string())
                server.quit()

                print 'Send alarm: ', machines, ' (recipients: ', ', '.join(toAddrs) , ')'

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
    parser.add_option('-a', '--alarm-threshold', dest='alarmThreshold', help='The threshold minutes to send alarm email by Gmail if the time passed since last update time is longer than it (default: 30)')
    parser.add_option('-g', '--gmail-addr', dest='gmailAddr', help='The administrator\'s Gmail')
    parser.add_option('-u', '--username', dest='userName', help='The administrator\'s Gmail username')
    parser.add_option('-s', '--password', dest='passWord', help='The administrator\'s Gmail password')
    parser.add_option('-r', '--recipients', dest='recipients', help='List of recipients\' emails other than the administrator, separated by semicolon.')
    (options, args) = parser.parse_args()

    port = options.port
    if not options.port:   # if port is not given, use the default one 
      port = 1666

    global alarmThresholdInMinutes
    global adminGmail
    global adminGmailUsername
    global adminGmailPassword
    global mailRecipients

    if options.alarmThreshold:
        alarmThresholdInMinutes = options.alarmThreshold

    if options.gmailAddr:
        if not options.userName or not options.passWord or not options.recipients:
            parser.error('Gmail setting is not completed.')
        adminGmail = options.gmailAddr
        adminGmailUsername = options.userName
        adminGmailPassword = options.passWord.replace('\\', '')
        mailRecipients = options.recipients.split(';')
   
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

