#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Yuanji
# Date Time: 2015-04-22 15:36:00
#
###############################################################################
import json
import uuid
import urllib
import tornado.web
import tornado.ioloop
from settings import *
from tornado import gen
import tornado.httpserver
from handlers.cookiehandler import *
import random, time, os, sys, socket
from collections import defaultdict
from utils.general import INTER_MSG_CLICK
from utils.general import *

import logging
logger = logging.getLogger(__name__)

IMG_FILE = open('./1x1.gif','r')
try:
    IMG_DATA = IMG_FILE.read()
finally:
    IMG_FILE.close()


class SuperClickHandler(tornado.web.RequestHandler):
    def initialize(self, broker):
        self.broker = broker
        self.cookiehandler = self.broker.cookie
        self.ob_msg_server = broker.msg_server

    def prepare(self):
        self.set_header('Pragma', 'no-cache')
        self.set_header("Cache-Control", 'no-cache,no-store,must-revalidate')
        self.set_header('P3P','CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"')

    def getIp(self):
        try:
            ipaddr = self.request.remote_ip
            self.dic['ip'] = ipaddr
        except Exception:
            pass

    def recordClick(self):
        try:
            rtb_type = self.dic["unionid"] if self.dic.has_key("unionid") else None
            tid = self.dic['adx_uid'] if self.dic.has_key("adx_uid") else None
            eid = self.dic["executeid"] if self.dic.has_key("executeid") else None
            pid = self.dic["pid"] if self.dic.has_key('pid') else None
            aid = self.dic['advid'] if self.dic.has_key('advid') else None
            if eid and pid:
                self.broker.database.incEidClick(eid,1)
                self.broker.database.incEidPidClick(eid, pid )
                logger.debug("increase Order Click OK!")
            return True
        except Exception, e:
            logger.error('SuperClickHandler/recordClick: %s'% e)
            return False

    def userClickRecord(self):
        try:
            if self.dic.has_key('advid'):
                userkey = USER_CLICK_RECORD % (self.ucookie, self.dic['advid'])
                info = json.dumps(self.dic)
                self.broker.database.setUserClickInfo(userkey, int(self.time), info)
                logger.debug("userClickRecord OK:  key->%s  field:%d  value:%s" % (userkey, int(self.time), info))
        except Exception, e:
            logger.error("userClickRecord:%s" % e)
            return False

    def sendMsg(self):
        try:
            self.ob_msg_server.sendMsgToStat(T_CLK, self.dic)
        except Exception,e:
            logerr.error("SuperClickHandler: SendMsg Err :%s" % e)

    def dealCookie(self):
        try:
            # cookie identify
            self.ucookie = self.get_cookie(DEF_USER_COOKIE)
            if not self.ucookie:
                self.ucookie = self.cookiehandler.setCookie()
                self.set_cookie(DEF_USER_COOKIE, self.ucookie, domain=DOMAIN, expires_days=UC_EXPIRES)
            else:
                if not self.cookiehandler.checkCookie(self.ucookie):
                    logger.error("UserCookie:%s is illegal!" % self.ucookie)
                    self.ucookie = self.cookiehandler.setCookie()
                    self.set_cookie(DEF_USER_COOKIE, self.ucookie, domain=DOMAIN, expires_days=UC_EXPIRES)
            self.dic['userid'] = self.ucookie
            logger.debug('cookie:%s' % self.dic['userid'])
        except Exception:
            pass  

    def getUriPar(self):
        self.dic['unionid'] = self.get_argument('x', default = "")
        self.dic['executeid'] = self.get_argument('e', default = "")
        self.dic['creativeid'] = self.get_argument('c', default = "")
        self.dic['pid'] = self.get_argument('s', default = "")
        self.dic['areaid'] = self.get_argument('a', default = DEFAULT_AREA)
        self.dic['advid'] = self.get_argument('d', default = "")
        self.dic['rid'] = self.get_argument('r', default = "")
        self.dic['bid_price'] = self.get_argument('b', default = "")
        self.dic['adx_uid'] = self.get_argument('u', default = "")
        self.dic['referer'] = self.get_argument('f', default = "")
        self.of = self.get_argument('of', default = OF_FLAG_JSON)
        self.aurl = self.get_argument("url", default = None)

    def returnGif(self):
        self.set_header('Content-Type', 'image/gif')
        self.write(IMG_DATA)

    def dealRedirect(self):
        self.dic['click_sourceid'] = random_str()
        if self.aurl:
            logger.info("Url:%s" % self.aurl)
            self.redirect(self.aurl)
        else:
            logger.info('No Url')

    def get(self):
        try:
            logger.debug("-------------CORE CLICK HANDLER----------------")
            self.dic = defaultdict()
            self.dic['type'] = INTER_MSG_CLICK
            self.time = int(time.time())
            self.dic['t'] = str( self.time )

            self.getIp()
            self.dealCookie()
            self.getUriPar()
            self.dealRedirect()
            self.recordClick()
            self.userClickRecord()
            self.sendMsg()

            #print aurl
            logger.debug("-----------------------------------------------")
        except Exception, e:
            logger.error(e)
            self.redirect(self.aurl)
            #self.dealRedirect()
            return

