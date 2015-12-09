#!/usr/bin/env python
#-*- coding:utf-8 -*-

###################################################
#
# Create by:  Wang Songting
# Date Time:  2012-11-06 14:42:58
# Content:    Handler Http request for log statistic.
# Notice : not note msg ,only send msg to kfaka
#
###################################################

import random, time, os, sys, socket
import tornado.ioloop
import tornado.httpserver
import tornado.web
from scheduler.log import init_syslog, logimpr, logclick, dbg, logwarn, logerr, _lvl

import settings
import urllib
import base64
import hashlib
import binascii
from copy import deepcopy
from settings import *
from generalhandler import * 
from cpahandler import * 
from collector import *
from countercache import *
#import MySQLdb
from priceparser.priceparser import AdxPriceParser

uc_expires = 5000
ad_expires = 1
RESPONSE_BLANK = """(function(){})();"""
LOG_OK = 'ok'
LOG_FAIL = 'fail'
REAL_IP = 'X-Real-Ip' # Need to config in nginx
REMOTE_IP = 'remote_ip'
REFERER = 'Referer'
USER_AGENT = 'User-Agent'
RECORD = "mRec"
error_times = 0
former_time = time.time()
limit_time = 10*60.0
REDIRECT_URL = "http://tanxlog.istreamsche.com/geo.jpg"


def SOCK():
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #soc.bind((server_ip, port))
        dbg("Socket created Ok!")
        return soc
    except socket.error, msg:
        logerr( 'Failed to create socket:%s' % msg )
        sys.exit()

def error_statistic():
    global error_times
    global former_time
    error_times += 1
    now = time.time()
    if (now - former_time) >= limit_time:
        former_time = now
        logerr("Log error times: %d,please check errors." % error_times)

def urlsafe_b64encode(string):
    encoded = base64.urlsafe_b64encode(string)
    return encoded.replace( '=', '' )

def urlsafe_b64decode(s):
    mod4 = len(s) % 4
    if mod4:
        s += ((4 - mod4) * '=')
    return base64.urlsafe_b64decode(str(s))


class DefaultHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        dbg('Default Handler.') 
        self.write(RESPONSE_BLANK)

class SuperActiveHandler(tornado.web.RequestHandler):
    def initialize(self, broker):
        self.broker = broker
    
    def get(self):
        try:
            conn=MySQLdb.connect(host='192.168.167.203',user='statdb',passwd='geotmt',db='statdb',port=3306)
            cur=conn.cursor()
            msg = defaultdict()
            msg['appid']       = self.get_argument('appid', default = "null")
            msg['idfa']        = self.get_argument('idfa', default = "null")
            msg['timestamp']   = self.get_argument('timestamp', default = "null")
            msg['adid']        = self.get_argument('adid', default = "null")
            msg['recvtime']    = time.strftime( '%Y-%m-%d %X', time.localtime() )
            sqli = "insert into stat_register_mobile (recvtime, appid, idfa, timestamp, adid) values (%s,%s,%s,%s,%s)"
            cur.execute(sqli, (msg['recvtime'], msg['appid'], msg['idfa'], msg['timestamp'], msg['adid']))
            conn.commit()
            cur.close()
            conn.close()
        except MySQLdb.Error,e:
            logerr("Mysql Error: %s" % (msg))
        self.write('1')
    
class Application(tornado.web.Application):
    def __init__(self, broker):
        handlers = [
            (r'/wbshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/wbclick.*',SuperClickHandler, dict(broker = broker)),		
            (r'/gdtshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/gdtclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/inmoshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/inmoclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/soshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/soclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/tshow',SuperShowHandler, dict(broker = broker)),
            (r'/tclick',SuperClickHandler, dict(broker = broker)),
            (r'/ayclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/ayshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/ykclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/ykshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/mgclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/mgshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/amshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/amclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/tdshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/tdclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/saxshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/saxclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/besshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/besclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/jxshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/jxclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/mzshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/mzclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/gyshow.*',SuperShowHandler, dict(broker = broker)),
            (r'/gyclick.*',SuperClickHandler, dict(broker = broker)),
            (r'/active.*',SuperActiveHandler, dict(broker = broker)),
            (r'/t',CollectorHandler, dict(broker = broker)),
            (r'/gm.gif*',CPAHandler, dict(broker = broker)),
            (r'/gmtest.gif*',CPAHandler, dict(broker = broker)),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "/var/www"}),
            (r'/(.*)',DefaultHandler)
        ]

        tornado.web.Application.__init__(self,handlers)

class HttpLoop(object):
    def __init__(self, broker):
        self.broker = broker
        self.port = broker.server_port
        self.proj_id = str(broker.proj_id)
        self.server_id = str(broker.server_id)

        pass
    def listen(self):
        try:
            http_server = tornado.httpserver.HTTPServer(Application(broker),xheaders=True)
            http_server.listen(self.port)
            return True
        except Exception, e:
            logerr("listen: %s" % e)
            return False

    def bind(self):
        try:
            http_server = tornado.httpserver.HTTPServer(Application(broker),xheaders=True)
            http_server.bind(self.port)
            http_server.start(num_processes=10)    
            return True
        except Exception, e:
            logerr("bind: %s" % e)
            return False

    def loop(self):
        tornado.ioloop.IOLoop.instance().start()

class Broker(object):
    def __init__(self):
        self.path = ''
        self.proj_id = int(sys.argv[1])
        self.server_id = int(sys.argv[2])
        self.server_list = []
        self.server_port = None
        self.global_shownum = 0
        self.sender = SOCK()
        self.adxPriceParser = AdxPriceParser()
        self.msglist = list()

        self.cookie = CookieHanlder( self.server_id, self.proj_id)

        self.cache_queue = CounterCacheQueue

    def daemonize(self):
        pid = os.fork()
        if pid < 0:
            os._exit(1)
        if pid > 0:
            os._exit(0)

        os.umask(0)
        os.setsid()

        pid = os.fork()
        if pid < 0:
            os._exit(1)
        if pid > 0:
            os._exit(0)

        for i in range(0,100):
            try:
                os.close(i)
            except Exception, e:
                pass
        file('/dev/null','r')
        file('/dev/null','a+')
        file('/dev/null','a+')

    def succ(self):
        sock_file = '%s/sock' % self.path
        s = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        s.sendto('True',sock_file)
        s.close()

    def fail(self):
        sock_file = '%s/sock' % self.path
        s = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
        s.sendto('False',sock_file)
        s.close()

    def pid_file_init(self):
        pid_path = '%s/pid' % self.path
        pid_file = '%s/log%u.pid' % (pid_path,int(self.server_id))
        f = open(pid_file,'w')
        f.write('%u\n' % self.pid)
        f.close()

if __name__ == '__main__':
    path = os.path.abspath(os.path.dirname(__file__))
    broker = Broker()
    broker.path = path
    broker.proj_id = int(sys.argv[1])
    broker.server_id = int(sys.argv[2])

    for server_id, port in settings.SHOW_SERVER:
        broker.server_list.append((server_id, port))
        if int(server_id) == broker.server_id:
            broker.server_port = port

    # Create Schd daomonize
    #if _lvl != 0:
    #    broker.daemonize()

    from scheduler.database import Database
    broker.database = Database()#Don't Use DAP Function

    CounterCacheQueueHandle()

    broker.pid = os.getpid()
    broker.pid_file_init()
    init_syslog()
   
    # Start HttpSock Thread
    http = HttpLoop(broker)
    if not http.listen():
        broker.fail()
        os._exit(1)
    broker.succ()
    http.loop()
    

