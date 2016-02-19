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
        self.adxPriceParser = broker.adxPriceParser
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
            self.ucookie = self.get_cookie(DEF_USER_COOKIE)
            if not self.ucookie:
                self.ucookie = self.cookiehandler.setCookie()
                self.set_cookie(DEF_USER_COOKIE, self.ucookie, domain=DOMAIN, expires_days=UC_EXPIRES)
            else:
                if not self.cookiehandler.checkCookie(self.ucookie):
                    logger.warn("UserCookie:%s is illegal!" % self.ucookie)
                    self.ucookie = self.cookiehandler.setCookie()
                    self.set_cookie(DEF_USER_COOKIE, self.ucookie, domain=DOMAIN, expires_days=UC_EXPIRES)
            self.dic['userid'] = self.ucookie
            logger.debug('cookie:%s' % self.dic['userid'])
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
            logger.warn('SuperShowHandler/parsePrice: %s' % e)
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
            #if pid and tid and eid:
            #    sendUserFreq(rtb_type, tid, eid, pid)
            #else:
            #    pass
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
            self.ob_msg_server.sendMsgToStat(T_IMP, self.dic)
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
        '''
        create_dic = {
            CRT_KEY_TYPE : 'img',
            CRT_KEY_MONITOR_URL : '',
            CRT_KEY_MATERIALS:[ { CRT_KEY_WIDTH:'300', CRT_KEY_HEIGHT:'250', CRT_KEY_CLICK_URL:'http://www.hao123.com',\
                                CRT_KEY_URL:'http://123.56.15.234/data/creative_files/1/1/5de39424bfa942b8aaecdeee97b1b58e.jpg',}]

        }'''
        '''get create detail '''
        create_dic = None
        if self.dic.has_key(PARA_KEY_CID):
            create_dic = self.broker.createcache.getCreateDetail(self.dic[PARA_KEY_CID])
        else:
            logger.warn('Has No CreateID!')

        if create_dic is None:
            logger.error('CreateID:%r is Not In Configure!' % self.dic[PARA_KEY_CID])
        else:
            if self.of == OF_FLAG_JSON:
                back = creatDspAdBack(self.dic, create_dic)
                logger.debug(back)
                self.write(back)

        self.finish()

    def paraCheck(self):
        if not is_num_by_except(self.dic[PARA_KEY_CID]):
            logger.warn("CreateID is no except num:%r" % self.dic[PARA_KEY_CID])
            return False
        if not is_num_by_except(self.dic[PARA_KEY_ADX]):
            logger.warn("UnionID is no except num:%r" % self.dic[PARA_KEY_ADX])
            return False
        return True

    def getUriPar(self):
        self.dic['unionid'] = self.get_argument('x', default = 0)
        self.dic['executeid'] = self.get_argument('e', default = "")
        self.dic['creativeid'] = self.get_argument('c', default = "")
        self.dic['pid'] = self.get_argument('s', default = "")
        self.dic['areaid'] = self.get_argument('a', default = DEFAULT_AREA)
        self.dic['advid'] = self.get_argument('d', default = "")
        self.dic['rid'] = self.get_argument('r', default = "")
        self.dic['bid_price'] = self.get_argument('b', default = "")
        self.dic['adx_uid'] = self.get_argument('u', default = "")
        self.dic['xcurl'] = self.get_argument('l', default = "")
        self.of = self.get_argument('of', default = OF_FLAG_JSON)
        #print self.dic

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
            self.time = int(time.time())
            self.dic['t'] = str( self.time )
            price = self.get_argument("p", default = '')

            if not self.paraCheck():
                return 

            if price:
                self.adx = int(self.dic['unionid'])
                self.parsePrice(str(price))
                self.dic['exchange_price'] = str(self.real_price)

            self.record(self.dic)
            self.sendMsg()

            self.customResult()

            logger.debug("---------------------------------------------")
            return
        except Exception, e:
            logger.error("SuperShowHandler Err:%s request:%r" % (e, self.request))
            return

