#!/usr/bin/env python
import tornado.httpserver
import tornado.ioloop
import tornado.web
import optparse
import logging
import traceback
import os

"""
Logging settings
"""
logger = logging.getLogger('DynIPReport')
logger.setLevel(logging.INFO)
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



            # send response json
            response = { 'result': 'OK'}
            self.write(response)

            print response

        except:
            tb = traceback.format_exc()
            errMsg = { 'error': tb }
            self.write(errMsg)
            logger.error(tb)

"""
Handles the summary page for adminstrator.
"""
class SummaryReportHanlder(tornado.web.RequestHandler):
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
                    (r"/summary", SummaryReportHanlder),
                    (r'/img/(.*)',tornado.web.StaticFileHandler,{'path':"website/img"}),
                    (r'/css/(.*)',tornado.web.StaticFileHandler,{'path':"website/css"}),
                    (r'/js/(.*)',tornado.web.StaticFileHandler,{'path':"website/js"})])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    print "Dynamic IP Report Service starts at port " + str(port) + "."
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

