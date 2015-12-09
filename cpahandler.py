#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Wang Songting
# Date Time: 2014-01-03 15:36:00
# Content:  service for loging register action.
#
###############################################################################
import random, time, os, sys, socket
import tornado.ioloop
import tornado.httpserver
import tornado.web
from scheduler.log import init_syslog, logimpr, logclick, loginfo,dbg, logwarn, logerr, _lvl
import settings
from settings import *
import urllib
import binascii
import json
from collections import defaultdict

error_times = 0
former_time = time.time()
limit_time = 10*60.0

#STATICGIF = 'http://gd.geotmt.com/g.gif'
NOMORL_GIF = 'http://sslcdn.geotmt.com/g.gif'
STATIC_GIF = 'https://sslcdn.geotmt.com/g.gif'
USER_CLICK_RECORD = "user:click:%s:aid:%s"
USER_ARRI_RECORD = "user:arrive:%s:rid:%s"

REFERER = 'Referer'
USER_AGENT = 'User-Agent'


GIF_FD = open("1x1.gif",'r')
GIF_CONTENT = GIF_FD.read()
GIF_FD.close()

def error_statistic():
    global error_times
    global former_time
    error_times += 1
    now = time.time()
    if (now - former_time) >= limit_time:
        former_time = now
        logerr("Log %s error times: %d,please check errors." % (os.getpid(), error_times))

def urlsafe_b64encode(string):
    encoded = base64.urlsafe_b64encode(string)
    return encoded.replace( '=', '' )

def urlsafe_b64decode(s):
    mod4 = len(s) % 4
    if mod4:
        s += ((4 - mod4) * '=')
    return base64.urlsafe_b64decode(str(s))
    
def promsg(uc, log, price):
    try:
        msg = defaultdict()
        msg['exchange_price'] = float(price)
        msg['ishow_id'] = settings.DEVICE_ID
        msg['ck_id'] = uc
        msg['imp_time'] = long(time.time()*1000)
        msg['region'] = log['aid']
        msg['size'] = '300x250'
        msg['adver_id'] = str(log['uid']) if log.has_key('uid')  else None
        msg['execute_id'] = str(log['eid']) if log.has_key('eid')  else None
        msg['creative_id'] = log['cid'] if log.has_key('cid') else None
        #msg['req_id'] = log['rid'] if log.has_key('rid') else None
        msg['req_id'] = str(random.randint(10000000,90000000))
        #msg['adx_id'] = int(log['xid']) if log.has_key('xid') else None
        msg['adx_id'] = 0
        msg['bid_price'] = float(price)
        msg['bid_core_id'] = '10000'
        msg['pid'] = "AITOU_PID_00000"
        #msg['pid'] = log['pid'] if log.has_key('pid') else None
        msg['target_price'] = str(price)
        msg['bid_mode'] = '1'
        msg['adx_uid'] = uc
        dbg(msg)
        return msg
    except Exception,e:
        logerr(e)
        return None

class CPAHandler(tornado.web.RequestHandler):
    def initialize(self, broker):
        self.broker = broker

    def prepare(self):
        self.set_header('P3P','CP="CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR"')

    def packInfo(self):
        try:      
            log_list = dict()
            #if referer and executeid and uid:
            log_list["t"] = long(self.time*1000)
            log_list["rid"] = self.rid
            log_list["uid"] = int(self.gtmac)
            log_list["eid"] = int(self.eid)
            log_list["xid"] = int(self.xid)
            log_list["pid"] = self.pid
            log_list["aid"] = self.aid
            log_list["cid"] = self.cid
            log_list["kw"] = self.kw
            log_list["tp"] = self.tp
            log_list["ct"] = self.ct
            log_list["od"] = self.od
            self.mn = self.mn.replace("￥","")
            self.mn = self.mn.replace("{","")
            self.mn = self.mn.replace("}","")
            log_list["mn"] = self.mn
            log_list["zid"] = self.zid
            log_list["id1"] = self.id1
            log_list["id2"] = self.id2
            log_list["id3"] = self.id3
            log_list["id4"] = self.id4
            log_list["id5"] = self.id5
            log_list["id6"] = self.id6
            log_list["id7"] = self.id7
            log_list["id8"] = self.id8
            log_list["id9"] = self.id9
            log_list["id10"] = self.id10    
            log_list["ua"] = self.ua
            log_list["ref"] = self.referer
          
            dbg(str(log_list))
            dbg('packinfo ok')
            return log_list
            
        except Exception, e:
            error_statistic()
            logerr('CPAHandler/packageInfo: %s'%e)
            return log_list

    def record(self, msg):
        try:
            if msg.has_key('eid') and msg.has_key('pid'):
                eid = msg['eid']
                pid = msg['pid']
                if self.tp == 1:
                    self.broker.database.incPidArri(eid, pid)
                if self.tp == 2:
                    self.broker.database.incPidReg(eid, pid)
        except Exception,e:
            logerr('CPA record:%s' % e)

    def priceImitation(self, msg):
        price = int(self.target_price) * random.uniform(0.9,1.1)
        imp_num = random.randint(2000,2500)
        cpm_price = int( float(price)/imp_num*1000 )
        remsg = promsg(self.uc, msg, cpm_price)
        #'''
        self.broker.database.incEidHourSp(str(msg['eid']), cpm_price * imp_num)
        self.broker.database.incEidHourPv(str(msg['eid']), imp_num)
        self.broker.database.incAdvBidSpend(str(msg['uid']), price)
        self.broker.database.decAdvBidSpend(str(msg['uid']), "-%.3f" % (float(price),))
        #'''
        self.sendImitationMsg(remsg,imp_num)
        loginfo("ImitationCPA:%s    price:%d  cpm_price:%d  imp_num:%d" % (remsg, price, cpm_price, imp_num))

    def sendImitationMsg(self, msg, num):
        try:      
            self.key = "CPA_Imitation"
            for i in xrange(num):
                self.broker.msglist.append(msg)
            if not self.broker.database.sendMsgToStat(T_IMP, self.key, self.broker.msglist): 
                logerr("SuperShowHandler: SendMsg Err :%s" % self.broker.msglist)
            else:
                pass
            self.broker.msglist = list()
        except Exception,e:
            logerr("sendImitationMsg Err:%s" % e)

    def sendCPAMsg(self, msg):
        try:
            self.broker.database.sendMsgToStat(T_CPA, "geo", msg)
            dbg('SendCPAMsg OK!')
        except Exception,e:
            logerr("CPAHandler: SendCPAMsg Err :%s" % e)
        
    def dealUserArriInfo(self):
        try:
            if self.bid_mode == "10000":
                return True
            if not self.uc:
                return True
            if self.broker.database.getUserArriInfo( USER_ARRI_RECORD % (self.uc, self.rid)):
                loginfo("User Have Arrive Info: %s" % ( USER_ARRI_RECORD % (self.uc, self.rid), ) )
                return False
            else:
                self.broker.database.setUserArriInfo( USER_ARRI_RECORD % (self.uc, self.rid), int(self.time))
                loginfo("Set User Arrive Info: %s" % ( USER_ARRI_RECORD % (self.uc, self.rid), ) )
                return True
        except Exception, e:
            logerr("dealUserArriInfo:%s" % e)
            return False

    def getUserClickRecord(self):
        try:
            if self.gtmac and self.uc:
                dbg("user:%s adverid:%s" % (self.uc, self.gtmac))
                user_msg = self.broker.database.getUserClickInfo( USER_CLICK_RECORD % (self.uc, self.gtmac))
                if user_msg:
                    user_msg = sorted(user_msg.iteritems(), key = lambda pd:pd[0], reverse = True)
                    loginfo("user click record:%s" % user_msg)
                    if len(user_msg) > 0:
                        tm = user_msg[0][0]
                        val = user_msg[0][1]
                        val = json.loads(val)
                        dbg("Chose Click Time:%s" % (tm,))
                        self.ct = int(tm)*1000
                        if val.has_key('adver_id'):
                            pass
                        if val.has_key('adx_id'):
                            self.xid = val['adx_id']
                        if val.has_key('execute_id'):
                            self.eid = val['execute_id']
                        if val.has_key('creative_id'):
                            self.cid = val['creative_id']
                        if val.has_key('region'):
                            self.aid = val['region']
                        if val.has_key('pid'):
                            self.pid = val['pid']
                        if val.has_key('req_id'):
                            self.rid = val['req_id']
                        if val.has_key('bid_mode'):
                            self.bid_mode = val['bid_mode']
                        if val.has_key('target_price'):
                            self.target_price = val['target_price']
                                
                        return True
            return False
        except Exception, e:
            logerr(e)
            return False
    # Redirect Handler
    def cusRedirect(self):
        if self.request.protocol == 'https':
            self.redirect(STATIC_GIF)
            return
        self.set_header('Content-Type', 'image/gif')
        self.write(GIF_CONTENT)
        #else:
        #    self.redirect(NOMORL_GIF)

    def recordMoney(self):
        try:
            loginfo("AdverTransaction Info advid %d money %s uc %s" % (int(self.gtmac), self.mn, self.uc))
        except Exception:
            pass

    def recordReg(self):
        try:
            loginfo("AdverReg Info advid %d od %s uc %s Referer %s" % (int(self.gtmac), self.od, self.uc, self.referer))
        except Exception:
            pass

    def get(self):
        try:
            dbg("-------------GEO CPA HANDLER----------------")
            #dbg(self.request)
            self.time = time.time()
            self.bid_mode = None
            self.gtmac = self.get_argument('gtmac', default = 0)
            self.rid = self.get_argument('rid', default = '')
            self.uid = int(self.get_argument('uid', default = 0))
            self.eid = int(self.get_argument('eid', default = 0))
            self.xid = int(self.get_argument('xid', default = 0))
            self.pid = self.get_argument('pid', default = '')
            self.aid = self.get_argument('aid', default = '')
            self.cid = self.get_argument('cid', default = '')
            self.kw = urllib.quote(self.get_argument('kw', default = ''))
            self.tp = int(self.get_argument('tp', default = 0))
            self.ct = int(self.get_argument('ct', default = 0))
            self.od = self.get_argument('od', default = '')
            self.mn = self.get_argument('mn', default = '').encode('utf-8')
            self.zid = self.get_argument('zid', default = '')
            self.id1 = self.get_argument('f1', default = '')
            self.id2 = self.get_argument('f2', default = '')
            self.id3 = self.get_argument('f3', default = '')
            self.id4 = self.get_argument('f4', default = '')
            self.id5 = self.get_argument('f5', default = '')
            self.id6 = self.get_argument('f6', default = '')
            self.id7 = self.get_argument('f7', default = '')
            self.id8 = self.get_argument('f8', default = '')
            self.id9 = self.get_argument('f9', default = '')
            self.id10 = self.get_argument('f10', default = '')
            self.referer = REFERER in self.request.headers and self.request.headers[REFERER] or ''
            self.ua  = USER_AGENT in self.request.headers and self.request.headers[USER_AGENT] or ''
            self.ua = urllib.quote(self.ua)
            self.uc = self.get_cookie('uc')

            if self.tp and self.tp == 1:
                self.gc = self.get_cookie('rck_s')
                #self.clear_cookie('rck_s')
            elif self.tp and self.tp != 1:
                self.gc = self.get_cookie('reg_l')
            else:
                self.gc = ''

            # get adverid
            if not self.gtmac and self.gc:
                self.gc = urllib.unquote(self.gc)
                gcs = self.gc.split(',')
                if len(gcs):
                    self.uid = int(gcs[1])  # Adver ID
                    self.gtmac = self.uid

            if self.tp == 3:
                self.recordMoney()

            if self.tp == 2:
                self.recordReg()

            # get user click history record
            if self.getUserClickRecord():
                msg = self.packInfo()
                if self.tp == 1:
                    if self.dealUserArriInfo():
                        self.record(msg)
                        self.sendCPAMsg(msg)
                        self.cusRedirect()
                    else:
                        self.cusRedirect()
                elif self.tp == 2 and self.bid_mode == "10000": # Qudao CPA
                    self.record(msg)
                    self.sendCPAMsg(msg)
                    self.priceImitation(msg)
                    self.cusRedirect()
                else:
                    self.record(msg)
                    self.sendCPAMsg(msg)
                    self.cusRedirect()
                return

            # no click record get from cookie
            if self.gc:
                self.gc = urllib.unquote(self.gc)
                dbg(self.gc)
                gcs = self.gc.split(',')
                if len(gcs):
                    self.rid = gcs[0]       # BID
                    self.uid = int(gcs[1])  # Adver ID
                    self.eid = int(gcs[2])  # EID
                    self.xid = int(gcs[3])  # Adx ID
                    self.pid = gcs[4]       # PID
                    self.aid = gcs[5]       # Area ID
                    self.cid = gcs[6]       # Create ID
                    self.kw = urllib.quote(gcs[7])
                    self.gtmac = self.uid
            else:
                dbg('No gc info')
                self.cusRedirect()
                return 

            if self.tp:
                msg = self.packInfo()
                if not msg:
                    self.cusRedirect()
                    return
                #print msg['uid']

                # Advertise ID Indefy
                if( self.gtmac and msg['uid'] and ( int(self.gtmac) != msg['uid'])):
                    self.cusRedirect()
                    return

                if( msg['eid'] or msg['uid'] or msg['cid']):
                    if self.tp == 1:
                        if self.dealUserArriInfo():
                            self.sendCPAMsg(msg)
                            self.record(msg)
                    else:
                        self.sendCPAMsg(msg)
                        self.record(msg)
                    #print msg
            self.cusRedirect()
            return
        except Exception, e:
            error_statistic()
            logerr('CPAHandler: %s'%e)
            self.cusRedirect()
            logerr(self.request)
            return False











