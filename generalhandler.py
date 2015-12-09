#!/usr/bin/env python
#-*- coding:utf-8 -*-

###################################################
#
# Create by:  WangSongting
# Date Time:  2014-12-29 16:03:00
# Content:    Handler Http request for log statistic.
# Notice : not note msg ,only send msg to kfaka
#
###################################################

import random, time, os, sys, socket
import tornado.ioloop
import tornado.httpserver
import tornado.web
from scheduler.log import init_syslog, logimpr, logclick, dbg,loginfo, logwarn, logerr, _lvl
import settings
import urllib,hmac
import base64
import hashlib
import binascii
from copy import deepcopy
from settings import SENDFREQ
from collections import defaultdict
from Crypto.Cipher import AES
from binascii import unhexlify, hexlify
from settings import *
from struct import *
import json
import datetime
import requests

p_list=['9050601115763100',
'1080865032378370000',
'mm_10982364_973726_8372451',
'mm_15191080_2147689_9068851',
'mm_48240557_4308325_29658791'
]


uc_expires = 5000
ad_expires = 1
RESPONSE_BLANK = """(function(){})();"""
LOG_OK = ''
LOG_FAIL = 'fail'
REAL_IP = 'X-Real-Ip' # Need to config in nginx
REMOTE_IP = 'remote_ip'
REFERER = 'Referer'
USER_AGENT = 'User-Agent'
DOMAIN = '.mtty.com'
STATICGIF = 'http://gd.geotmt.com/g.gif'

USER_CLICK_RECORD = "user:click:%s:aid:%s"

error_times = 0
former_time = time.time()
limit_time = 10*60.0

rtbser = dict()
SOC = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#socket

MCAST_GRP = '238.2.20.128'
MCAST_PORT_A = 14331
MCAST_PORT_B = 14333
MCSOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
MCSOCK.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

#Avro
try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter, BinaryEncoder, BinaryDecoder
from partchoice.partchoice import GtAdpLogsMd5
writers_schema = avro.schema.parse(open("./utils/impression.avsc").read())
show_writer = DatumWriter(writers_schema)

def partChoice(key):
    return GtAdpLogsMd5(key, PART_NUM)

def createAvro(content):
    writer = StringIO()
    encoder = BinaryEncoder(writer)    
    show_writer.write(content, encoder)
    return writer.getvalue()

def sendUserFreq(rtb_type, tid, eid, pid):   
    info = {"league":str(rtb_type), "userid": tid, "execid": eid, "pid": pid}   
    MCSOCK.sendto(json.dumps(info), (MCAST_GRP,MCAST_PORT_B))

def error_statistic():
    global error_times
    global former_time
    error_times += 1
    now = time.time()
    if (now - former_time) >= limit_time:
        former_time = now
        logerr("Show Log error times: %d,please check errors." % error_times)

def urlsafe_b64encode(string):
    encoded = base64.urlsafe_b64encode(string)
    return encoded.replace( '=', '' )

def urlsafe_b64decode(s):
    mod4 = len(s) % 4
    if mod4:
        s += ((4 - mod4) * '=')
    return base64.urlsafe_b64decode(str(s))

def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)

Encode = {
        0:['p','m','7','M','A','i','Y'],
        1:['a','F','j','2','v','X','2'],
        2:['K','b','E','E','R','f','L'],
        3:['o','8','1','d','w','S','1'],
        4:['5','G','k','5','u','W','T'],
        5:['Q','0','D','C','N','B','Z'],
        6:['n','H','c','3','3','V','e'],
        7:['J','s','l','t','x','U','x'],
        8:['r','9','6','O','z','h','6'],
        9:['q','4','P','4','y','g','I']
    }

Decode = {
        'p':'0','m':'0','7':'0','M':'0','A':'0','i':'0','Y':'0',
        'a':'1','F':'1','j':'1','2':'1','v':'1','X':'1',
        'K':'2','b':'2','E':'2','R':'2','f':'2','L':'2',
        'o':'3','8':'3','1':'3','d':'3','w':'3','S':'3',
        '5':'4','G':'4','k':'4','u':'4','W':'4','T':'4',
        'Q':'5','0':'5','D':'5','C':'5','N':'5','B':'5','Z':'5',
        'n':'6','H':'6','c':'6','3':'6','V':'6','e':'6',
        'J':'7','s':'7','l':'7','t':'7','x':'7','U':'7',
        'r':'8','9':'8','6':'8','O':'8','z':'8','h':'8',
        'q':'9','P':'9','4':'9','y':'9','g':'9','I':'9'
    }

    
class CookieHanlder():
    def __init__(self, server_id, proj_id):
        self.server_id = server_id
        self.proj_id = proj_id

        self.cookie_base1 = 100
        self.cookie_base2 = 1000
        
    def Encrypt(self, code):
        encode = [ random.choice(Encode[code[i]]) for i in xrange(32)]
        my_encode = ''.join(encode)
        return my_encode
    
    def Decrypt(self, code):
        try:
            decode = [ Decode[code[i]] for i in xrange(32)]
        except Exception, e:
            logerr(e)
            return False,0
        
        return True,decode
    
    def setVerifyCode(self, sn_in):
        sn = [ int(sn_in[i]) for i in xrange(24)]
        
        vv = 0              # sum of sn[0] to sn[23]
        v = 0
        for i in sn[0:8]:
            v += i
        sn.append(v / 10)   # sn[24,25] = sum of sn[0] to sn[7]
        sn.append(v % 10)
        vv += v
    
        v = 0
        for i in sn[8:16]:
            v += i
        sn.append(v / 10)   # sn[26,27] = sum of sn[8] to sn[15]
        sn.append(v % 10)
        vv += v
       
        v = 0
        for i in sn[16:24]:
            v += i
        sn.append(v / 10)   # sn[28,29] = sum of sn[16] to sn[23]
        sn.append(v % 10)
        vv += v
        
        v = vv % 100
        sn.append(v / 10)   # sn[30,31] = sum of sn[24] to sn[29]
        sn.append(v % 10)
        return sn
    
    def checkVerifyCode(self, sn_in):
        try:
            sn = [int(sn_in[i]) for i in xrange(32)]
        except Exception, e:
            logerr(e)
            return False
    
        v = 0
        for i in sn[0:8]:
            v += i
        if (v / 10) != sn[24]:
            return False
        if (v % 10) != sn[25]:
            return False
    
        v = 0
        for i in sn[8:16]:
            v += i
        if (v / 10) != sn[26]:
            return False
        if (v % 10) != sn[27]:
            return False
    
        v = 0
        for i in sn[16:24]:
            v += i
        if (v / 10) != sn[28]:
            return False
        if (v % 10) != sn[29]:
            return False
    
        v = sn[24]*10 + sn[25] + sn[26]*10 + sn[27] + sn[28]*10 + sn[29]
        vv = v % 100
        if (vv / 10) != sn[30]:
            return False
        if (vv % 10) != sn[31]:
            return False
    
        return True
    def setCookieBase(self):
        self.cookie_base1 += 1
        self.cookie_base2 += 1
        if self.cookie_base1 > 999:
            self.cookie_base1 = 100
        if self.cookie_base2 > 9999:
            self.cookie_base2 = 1000
            
    # Check User's Cookie is valid.
    def checkCookie(self, cookie):
        if len(cookie) != 32:
            return False
    	flag,verify_code = self.Decrypt(cookie)
        if not flag:
            return False
        return self.checkVerifyCode(verify_code)
    
    def setCookie(self):
        self.setCookieBase()
        sn = "%05u%03u%02u%04u%010.0f" % (self.server_id,self.cookie_base1,self.proj_id,self.cookie_base2,time.time())
        verify_code = self.setVerifyCode(sn)
        cookie = self.Encrypt(verify_code)
        return cookie

def ParseInfo(info):
    try:
        dbg(info)
        content = urlsafe_b64decode(info) 
        log = defaultdict()
        for con in content.split('\t'):
            dbg(con)
            try:
                f = con.find(":")
                key_str = con[0:f]
                con_str = con[(f+1) : ]
                log[key_str] = con_str
                
            except Exception as e:
                logwarn("key wrong:%s" % key_str)
                logerr('SuperShowHandler parseInfo(): Error Log Key %s' % key_str)
                continue
        dbg(log)
        return log

    except Exception, e:
        #logerr('SuperShowHandler/parseInfo:%s' % e)
        logwarn('InfoParseErr:%s' % info)
        return defaultdict()


class SuperShowHandler(tornado.web.RequestHandler):
    def initialize(self, broker):
        self.broker = broker
        self.adxPriceParser = broker.adxPriceParser
        self.cookiehandler =broker.cookie
        self.global_shownum = broker.global_shownum
        self.real_price = 0
        self.real_bid = ''
        self.adx = 0

    def prepare(self):
        self.set_header('Pragma', 'no-cache')
        self.set_header("Cache-Control", 'no-cache,no-store,must-revalidate')
        self.set_header('P3P','CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"')

    def parsePrice(self, en_msg):
        try:
            if not en_msg:
                self.real_price = 0
                return False
            else:
                self.real_price = self.adxPriceParser.parsePrice(self.adx, en_msg)
                if not self.real_price:
                    self.real_price = 0
                dbg('price: %s, %s' % (en_msg, str(self.real_price)))
                return True
        except Exception, e:
            self.real_price = 0
            error_statistic()
            logerr('SuperShowHandler/parsePrice: %s' % e)
            return False

    def record(self, msg):                   
        try:
            rtb_type = msg["unionid"]
            tid = msg['adx_uid']
            eid = msg["executeid"]
            pid = msg["pid"]
            dealprice = msg["exchange_price"]

            '''increase user freq'''
            if pid and tid and eid:
                sendUserFreq(rtb_type, tid, eid, pid)

            try:
                dc = defaultdict()
                dc['type'] = 1
                dc['eid'] = eid
                dc['pid'] = pid
                dc['price'] = int(dealprice)
                dc['aid'] = msg['advid']
                #loginfo(dc)
                self.broker.cache_queue.put(dc)
            except Exception,e:
                logerr(e)
            if msg.has_key("advid"):
                self.broker.database.incPidImpression(eid, pid )            
                self.broker.database.incPidExPrice(eid, pid,int( dealprice ) )             
            return True  
        except Exception, e:
            logerr('SuperShowHandler/record: %s' % e)
            return False
        
    def sendMsg(self, msg):
        try:
            if not self.broker.database.sendMsgToStat(T_IMP, msg):
                logerr("SuperShowHandler: SendMsg Err :%s" % msg)
            dbg('Send Or Create Log_Msg_List OK!')
        except Exception,e:
            logerr("SuperShowHandler: SendMsg Err :%s" % e)

    def getAdxID(self):
        self.path = self.request.path
        #loginfo('path:%s' % self.path)
        if ADX_BES in self.path:
            self.adx = ADX_BES_ID
        elif ADX_TANX in self.path:
            self.adx = ADX_TANX_ID
        elif ADX_SOHU in self.path:
            self.adx = ADX_SOHU_ID
        elif ADX_YICH in self.path:
            self.adx = ADX_YICH_ID
        elif ADX_MMAX in self.path:
            self.adx = ADX_MMAX_ID
        elif ADX_SINA in self.path:
            self.adx = ADX_SINA_ID
        elif ADX_YUKU in self.path:
            self.adx = ADX_YUKU_ID
        elif ADX_TENC in self.path:
            self.adx = ADX_TENC_ID
        elif ADX_AMAX in self.path:
            self.adx = ADX_AMAX_ID
        elif ADX_INMO in self.path:
            self.adx = ADX_INMO_ID
        elif ADX_JUXI in self.path:
            self.adx = ADX_JUXI_ID
        elif ADX_MIZH in self.path:
            self.adx = ADX_MIZH_ID
        elif ADX_GYIN in self.path:
            self.adx = ADX_GYIN_ID
        elif ADX_GDT in self.path:
            self.adx = ADX_GDT_ID
        elif ADX_WEIBO in self.path:
            self.adx = ADX_WEIBO_ID
        dbg('adexchange id : %d' % self.adx)

    def get(self,*args, **kwargs):
        dbg('==============GEO BIDDING SUPER SHOW HANDLER==============')
        try:
            self.dic = defaultdict()
            self.dic['t'] = str(int(time.time()))
            price = self.get_argument("p", default = '')
            self.getAdxID()

            self.ucookie = self.get_cookie('m')
            if not self.ucookie:
                self.ucookie = self.cookiehandler.setCookie()
                self.set_cookie("m", self.ucookie, domain=DOMAIN, expires_days=uc_expires)
            else:
                if not self.cookiehandler.checkCookie(self.ucookie):
                    dbg("UserCookie:%s is illegal!" % self.ucookie)
                    self.ucookie = self.cookiehandler.setCookie()
                    self.set_cookie("m", self.ucookie, domain=DOMAIN, expires_days=uc_expires)
             
            if price:
                self.parsePrice(str(price))
                self.dic['exchange_price'] = str(self.real_price)

            self.dic['userid'] = self.ucookie
            self.dic['unionid'] = self.adx
            self.dic['executeid'] = self.get_argument('e', default = "")
            self.dic['creativeid'] = self.get_argument('c', default = "")
            self.dic['pid'] = self.get_argument('s', default = "")
            self.dic['areaid'] = self.get_argument('a', default = "")
            self.dic['advid'] = self.get_argument('d', default = "")
            self.dic['rid'] = self.get_argument('r', default = "")
            self.dic['bid_price'] = self.get_argument('b', default = "")
            self.dic['adx_uid'] = self.get_argument('u', default = "")

            self.record(self.dic)
            self.sendMsg(self.dic)

            return             
        except Exception,e:
            error_statistic()
            logerr('SuperShowHandler: %s' % e)
            return

class SuperClickHandler(tornado.web.RequestHandler):
    def initialize(self, broker):
        self.broker = broker
        self.cookiehandler = broker.cookie
    
    def prepare(self):
        self.set_header('Pragma', 'no-cache')
        self.set_header("Cache-Control", 'no-cache,no-store,must-revalidate')
        self.set_header('P3P','CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"')

    def record(self, msg):
        try:
            eid = msg["executeid"]

            self.broker.database.incEidHourCk(eid)
            if msg.has_key('pid'):
                self.broker.database.incPidClick(eid, msg['pid'] )            
            dbg("increase Order ClickTimes OK!")
            return True
        except Exception, e:
            logerr('SuperClickHandler/parseInfo: %s'% e)
            return False

    def userClickRecord(self, info):
        try:
            if info.has_key('advid'):
                userkey = USER_CLICK_RECORD % (self.ucookie, info['advid'])
                info = json.dumps(info)
                self.broker.database.setUserClickInfo(userkey, int(self.time), info)
                dbg("userClickRecord OK:  key->%s  field:%d  value:%s" % (userkey, int(self.time), info))
        except Exception, e:
            logerr("userClickRecord:%s" % e)
            return False


    def sendMsg(self, msg):
        try:
            self.broker.database.sendMsgToStat(T_CLK, msg)
            dbg('Send Click Info OK!')
        except Exception,e:
            logerr("SuperClickHandler: SendMsg Err :%s" % e)

    def getAdxID(self):
        self.path = self.request.path
        dbg('path:%s' % self.path)
        if ADX_BES_CLICK in self.path:
            self.adx = ADX_BES_ID
        elif ADX_TANX_CLICK in self.path:
            self.adx = ADX_TANX_ID
        elif ADX_SOHU_CLICK in self.path:
            self.adx = ADX_SOHU_ID
        elif ADX_YICH_CLICK in self.path:
            self.adx = ADX_YICH_ID
        elif ADX_MMAX_CLICK in self.path:
            self.adx = ADX_MMAX_ID
        elif ADX_SINA_CLICK in self.path:
            self.adx = ADX_SINA_ID
        elif ADX_YUKU_CLICK in self.path:
            self.adx = ADX_YUKU_ID
        elif ADX_TENC_CLICK in self.path:
            self.adx = ADX_TENC_ID
        elif ADX_AMAX_CLICK in self.path:
            self.adx = ADX_AMAX_ID
        elif ADX_INMO_CLICK in self.path:
            self.adx = ADX_INMO_ID
        elif ADX_JUXI_CLICK in self.path:
            self.adx = ADX_JUXI_ID
        elif ADX_MIZH_CLICK in self.path:
            self.adx = ADX_MIZH_ID
        elif ADX_GYIN_CLICK in self.path:
            self.adx = ADX_GYIN_ID
        elif ADX_GDT_CLICK in self.path:
            self.adx = ADX_GDT_ID
        elif ADX_WEIBO_CLICK in self.path:
            self.adx = ADX_WEIBO_ID

    def get(self):
        try:
            dbg("-------------GEO Super Click HANDLER----------------")
            self.time = time.time()
            self.dic = defaultdict()
            aurl = self.get_argument('url', default = "")
            self.ucookie = self.get_cookie('m')
            self.getAdxID()
            if aurl:
                loginfo("url:%s" % aurl)
                self.redirect(aurl)

            if not self.ucookie:
                self.ucookie = self.cookiehandler.setCookie()
                self.set_cookie("m", self.ucookie, domain=DOMAIN, expires_days=uc_expires)

            self.dic['t'] = str(int(self.time))
            self.dic['userid'] = self.ucookie
            self.dic['unionid'] = self.adx
            self.dic['executeid'] = self.get_argument('e', default = "")
            self.dic['creativeid'] = self.get_argument('c', default = "")
            self.dic['pid'] = self.get_argument('s', default = "")
            self.dic['areaid'] = self.get_argument('a', default = "")
            self.dic['advid'] = self.get_argument('d', default = "")
            self.dic['rid'] = self.get_argument('r', default = "")

            self.record(self.dic)
            self.userClickRecord(self.dic)
            self.sendMsg(self.dic)
        except Exception, e:
            logerr("ClickHandler:%s" % e)




