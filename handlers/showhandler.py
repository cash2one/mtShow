#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Yuanji
# Date Time: 2015-04-22 15:36:00
#
###############################################################################
import uuid
import urllib
import tornado.log
import tornado.web
import tornado.ioloop
from settings import *
from tornado import gen

import random, time, os, sys, socket
from collections import defaultdict
from adrender import creatDspAdBack
from utils.general import *

import logging
logger = logging.getLogger(__name__)

IMG_FILE = open('./1x1.gif','r')
try:
    IMG_DATA = IMG_FILE.read()
finally:
    IMG_FILE.close()

REFERER = 'Referer'
USER_AGENT = 'User-Agent'


class SuperShowHandler(tornado.web.RequestHandler):
    def initialize(self, broker):
        self.res = None
        self.broker = broker
        self.cookiehandler = self.broker.cookie
        self.ob_msg_server = broker.msg_server
        self.real_price = 0
        self.adx = 0

    def prepare(self):
        self.set_header('Pragma', 'no-cache')
        self.set_header("Cache-Control", 'no-cache,no-store,must-revalidate')
        self.set_header('P3P','CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"')

    def getIp(self):
        try:
            ipaddr = self.request.remote_ip
            self.dic['ip'] = ipaddr
            logger.debug('ip:%s' % self.dic['ip'])
        except Exception:
            pass

    def dealCookie(self):
        try:
            # cookie identify
            if not self.ucookie:
                self.ucookie = self.cookiehandler.setCookie()
                self.set_cookie(DEF_USER_COOKIE, self.ucookie, domain=DOMAIN, expires_days=UC_EXPIRES)
            else:
                if not self.cookiehandler.checkCookie(self.ucookie):
                    logger.error("UserCookie:%s is illegal!" % self.ucookie)
                    self.ucookie = self.cookiehandler.setCookie()
                    self.set_cookie(DEF_USER_COOKIE, self.ucookie, domain=DOMAIN, expires_days=UC_EXPIRES)
            self.dic['uid'] = self.ucookie
            logger.debug('cookie:%s' % self.dic['uid'])
        except Exception:
            pass

    def parsePrice(self, en_msg):
        try:
            if not en_msg:
                self.real_price = 0
                return False
            else:
                self.real_price = self.adxPriceParser.parsePrice(self.adx, en_msg)
                if not self.real_price:
                    self.real_price = 0
                logger.debug('price: %s, %s' % (en_msg, str(self.real_price)))
                return True
        except Exception, e:
            self.real_price = 0
            logger.error('SuperShowHandler/parsePrice: %s' % e)
            return False

    def record(self, msg):
        try:
            rtb_type = msg["unionid"] if msg.has_key("unionid") else None
            tid = msg['adx_uid'] if msg.has_key("adx_uid") else None
            eid = msg["executeid"] if msg.has_key("executeid") else None
            pid = msg["pid"] if msg.has_key('pid') else None
            aid = msg['advid'] if msg.has_key('advid') else None
            dealprice = msg["exchange_price"] if msg.has_key('exchange_price') else 0
            '''increase user freq'''
            if pid and tid and eid:
                sendUserFreq(rtb_type, tid, eid, pid)
            else:
                pass
            try:
                if eid and pid and aid:
                    dc = defaultdict()
                    dc['type'] = 1
                    dc['eid'] = eid
                    dc['pid'] = pid
                    dc['price'] = int(dealprice)
                    dc['aid'] = aid
                    self.broker.countercache.queueMsgPut( dc )
                    #self.broker.database.incPidImpression(eid, pid )
                    #self.broker.database.incPidExPrice(eid, pid,int( dealprice ) )
            except Exception,e:
                logger.error('record:%s' % e)
            return True
        except Exception, e:
            logger.error('SuperShowHandler/record: %s' % e)
            return False

    def sendMsg(self):
        try:
            self.ob_msg_server.sendMsgToStat(T_IMP, self.dic):
            logger.debug('Send Or Create Log_Msg_List OK!')
        except Exception,e:
            logger.error("SuperShowHandler: SendMsg Err :%s" % e)

    def getAdxID(self):
        self.path = self.request.path
        self.adx = chooseAdxID(self.path)
        dbg('adexchange id : %d' % self.adx)

    def returnGif(self):
        self.set_header('Content-Type', 'image/gif')
        self.write(IMG_DATA)

    def customResult(self):
        self.set_header("Content-Type", "text/html")

        create_dic = {
            CRT_KEY_TYPE : 'img',
            CRT_KEY_MONITOR_URL : 'http://www.123.com',
            CRT_KEY_MATERIALS:[ { CRT_KEY_WIDTH:'300', CRT_KEY_HEIGHT:'250', CRT_KEY_CLICK_URL:'http://www.hao123.com'},
                                CRT_KEY_MATERIALS:'',]

        }
            back = creatDspAdBack(self.dic, create_dic)
        self.write(back)
        self.finish()

    def getUriPar(self):
        self.dic['userid'] = self.ucookie
        self.dic['unionid'] = self.get_argument('x', default = "")
        self.dic['executeid'] = self.get_argument('e', default = "")
        self.dic['creativeid'] = self.get_argument('c', default = "")
        self.dic['pid'] = self.get_argument('s', default = "")
        self.dic['areaid'] = self.get_argument('a', default = DEFAULT_AREA)
        self.dic['advid'] = self.get_argument('d', default = "")
        self.dic['rid'] = self.get_argument('r', default = "")
        self.dic['bid_price'] = self.get_argument('b', default = "")
        self.dic['adx_uid'] = self.get_argument('u', default = "")
        self.of = self.get_argument('of', default = OF_FLAG_JSON)

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        try:
            logger.debug("-------------SuperShowHandler HTTP HANDLER----------------")
            self.dic = defaultdict()

            self.getIp()
            self.dealCookie()
            self.getUriPar()
            self.dic['type'] = INTER_MSG_SHOW
            self.dic['t'] = str(int(time.time()))
            price = self.get_argument("p", default = '')
            if price:
                self.parsePrice(str(price))
                self.dic['exchange_price'] = str(self.real_price)

            self.record(self.dic)
            self.sendMsg(self.dic)

            self.customResult()

            logger.debug("---------------------------------------------")
            return
        except Exception, e:
            logger.error("SuperShowHandler Err:%s request:%r" % (e, self.request))
            self.customResult()
            return

