#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Yuanji
# Date Time: 2015-04-22 15:36:00
#
###############################################################################
import random, time, os, sys, socket
import tornado.ioloop
import tornado.httpserver
import tornado.web
from scheduler.log import init_syslog, logimpr, logclick, dbg, logwarn, logerr, _lvl
import settings
from settings import *
import urllib
import binascii
from generalhandler import *
#from showhandler import DOMAIN, RESPONSE_BLANK, LOG_OK

COL_VERSION = '1.0.0'

REFERER = 'Referer'
USER_AGENT = 'User-Agent'

def urlsafe_b64encode(string):
    encoded = base64.urlsafe_b64encode(string)
    return encoded.replace( '=', '' )

def urlsafe_b64decode(s):
    mod4 = len(s) % 4
    if mod4:
        s += ((4 - mod4) * '=')
    return base64.urlsafe_b64decode(str(s))
    

class CollectorHandler(tornado.web.RequestHandler):
    def initialize(self, broker):
        self.broker = broker
        self.cookiehandler = CookieHanlder(broker)

    def prepare(self):
        self.set_header('P3P','CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"')

    def packInfo(self):
        try:      
            log_list = dict()
            #log_list["t"] = long(self.time*1000)
            log_list["gmuid"] = self.ucookie
            log_list["gmv"] = COL_VERSION
            log_list["gmac"] = self.gmac
            log_list["gmh"] = urllib.quote_plus(self.gmh)
            log_list["gmp"] = urllib.quote_plus(self.gmp)
            log_list["gmcs"] = self.gmcs
            log_list["gmdt"] = self.gmdt
            log_list["gmrf"] = self.gmrf
            log_list["gmsc"] = self.gmsc
            log_list["gmsr"] = self.gmsr
            log_list["gmla"] = self.gmla
            log_list["gmrd"] = self.gmrd

            dbg(str(log_list))
            return log_list
            
        except Exception, e:
            error_statistic()
            logerr('CollectorHandler/packageInfo: %s' % e)
            return log_list

    def sendMsg(self, msg):
        try:
            self.broker.database.sendMsgToStat(T_COL, msg["gmuid"], msg)
        except Exception,e:
            logerr("CollectorHandler: SendCPAMsg Err :%s" % e)
        
    def get(self):
        try:
            dbg("-------------GEO CollectorHandler HANDLER----------------")
            self.time = time.time()
            self.ucookie = self.get_cookie('uc')

            # cookie identify
            if not self.ucookie:
                self.ucookie = self.cookiehandler.setCookie()
                self.set_cookie("uc", self.ucookie, domain=DOMAIN, expires_days=uc_expires)
            else:
                if not self.cookiehandler.checkCookie(self.ucookie):
                    dbg("UserCookie:%s is illegal!" % self.ucookie)
                    self.ucookie = self.cookiehandler.setCookie()
                    self.set_cookie("uc", self.ucookie, domain=DOMAIN, expires_days=uc_expires)

            if self.ucookie:
                self.gmv = self.get_argument('gmv', default = '')
                self.gmac = self.get_argument('gmac', default = '').encode('utf-8')
                self.gmh = self.get_argument('gmh', default = '').encode('utf-8')
                self.gmp = self.get_argument('gmp', default = '').encode('utf-8')
                self.gmcs = self.get_argument('gmcs', default = '').encode('utf-8')
                #self.gmdt = self.get_argument('gmdt', default = '').encode('utf-8')
                self.gmdt = ""
                self.gmrf = self.get_argument('gmrf', default = '').encode('utf-8')
                self.gmsc = self.get_argument('gmsc', default = '').encode('utf-8')
                self.gmsr = self.get_argument('gmsr', default = '').encode('utf-8')
                self.gmla = self.get_argument('gmla', default = '').encode('utf-8')
                self.gmrd = self.get_argument('gmrd', default = '').encode('utf-8')
                
                if not self.gmrf:
                    self.gmrf = REFERER in self.request.headers and self.request.headers[REFERER].encode('utf-8') or ''
                    #self.ua  = USER_AGENT in self.request.headers and self.request.headers[USER_AGENT] or ''
                msg = self.packInfo()   
                self.sendMsg(msg)
                return
        except Exception, e:
            logerr("CollectorHandler:%s" % e)
            return False

