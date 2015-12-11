#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import traceback,json
from utils.redisdb import RedisDb
from datetime import datetime
from time import localtime,strftime


class Database(object):
    def __init__(self, redis_conf = None):
        self.counter = 0
        self.red = None
        self.red_list = list()
        self.m_redis_conf = redis_conf
        self.hour = lambda : str(datetime.now().hour).zfill(2)
        #self.today = lambda : "%d-%2d-%02d" % (datetime.now().year, datetime.now().month, datetime.now().day)
        self.today = lambda : strftime("%Y-%m-%d", localtime())
        self.initDatabase()

    def initDatabase(self):
        if isinstance(self.m_redis_conf, tuple):
            for r in self.m_redis_conf:
                try:
                    self.red_list.append( RedisDb(r[0],r[1]) )
                except Exception, e:
                    print e

    def switch(self):
        #print self.red_list
        if self.counter < len(self.red_list):
            pass
        else:
            self.counter = 0
        self.red = self.red_list[self.counter]
        self.counter = self.counter + 1
    
    def expiretime(self):
        now = datetime.now()
        stringtime = "%s-%s-%s 23:59:59" % (now.year, now.month, now.day)
        tm = time.strptime(stringtime, "%Y-%m-%d %H:%M:%S")
        tm = int(time.mktime(tm))
        return tm

    def incUserHourPv(self, userid, eid, adx):
        try:
            if userid and eid and adx:
                self.switch()
                key = "user:pv:hour:%s:%s" %  (userid, adx)
                self.red._hincr(key, eid)
                self.red._expire(key, 3600)
        except Exception,e:
            print e

    def incUserDayPv(self, userid, eid, adx):
        try:
            if userid and eid and adx:
                self.switch()
                key = "user:pv:day:%s:%s" % ( userid, adx)
                self.red._hincr(key, eid)
                self.red._expireat(key, self.expiretime())
        except Exception,e:
            print e

    def incPidRequest(self, pid, num):
        try:
            if pid :
                self.switch()
                today = self.today()
                hour = self.hour()
                key = "pid:request:%s:%s" % (today, pid)
                self.red._hincrby(key, hour, num)
        except Exception,e:
            print e

    def incPidClick(self, pid, num):
        try:
            if pid :
                self.switch()
                today = self.today()
                hour = self.hour()
                key = "pid:click:%s:%s" % (today, pid)
                self.red._hincrby(key, hour, num)
        except Exception,e:
            print e

    def incEidClick(self, eid, num):
        try:
            if eid :
                self.switch()
                today = self.today()
                hour = self.hour()
                key = "eid:click:%s:%s" % (today, eid)
                self.red._hincrby(key, hour, num)
        except Exception,e:
            print e
    def incEidShow(self, eid, num):
        try:
            if eid :
                self.switch()
                today = self.today()
                hour = self.hour()
                key = "eid:show:%s:%s" % (today, pid)
                self.red._hincrby(key, hour, num)
        except Exception,e:
            print e

    def incPidImpression(self, eid, pid):
        try:
            self.switch()
            today = self.today()
            key = "exec:impression:pid:%s:%s" % (today, eid)
            return self.red._hincr(key, pid)

    def incEidPidClick(self, eid, pid):
        try:
            self.switch()
            today = self.today()
            key = "exec:click:pid:%s:%s" % (today, eid)
            return self.red._hincr(key, pid)

    def incPidExPrice(self, eid, pid, price):
        try:
            self.switch()
            today = self.today()
            key = "exec:exchangeprice:pid:%s:%s" % (today, eid)
            return self.red._hincrby(key, pid, price)

    def incPidPv(self, pid, eid):
        try:
            if pid and eid:
                self.switch()
                key = "pid:pv:%s" % (pid,)
                self.red._hincr(key, eid)
                self.red._expireat(key, self.expiretime())
        except Exception,e:
            print e

    def getOrderList(self):
        try:
            self.switch()
            return self.red._hkeys("exec:raw")
        except Exception, e:
            print e

    def getOrderInfo(self, orderid):
        try:
            self.switch()
            return self.red._hget("exec:raw", orderid)
        except Exception, e:
            print e

    def getAdvertiserMoney(self, advid):
        try:
            self.switch()
            money = self.red._get("adv:cash:%s" % advid)
            if money:
                return int(float(money))
            else:
                return 0
        except Exception, e:
            print "getAdvertiserMoney:%s" % e
            return 0

    def getOrderTodayMoney(self, orid):
        # total money ,this hour money
        try:
            self.switch()
            hour = self.hour()
            real_money = self.red._hgetall("exec:hourspend:%s" % orid)
            if real_money:
                havespend = hourspend = 0
                for tb in real_money.iteritems():
                    if tb[0] <= hour:
                        havespend = havespend + int(tb[1])/1000
                    if tb[0] == hour:
                        ''' hourspend '''
                        hourspend = int(tb[1])/1000
                return havespend, hourspend
            else:
                return 0, 0
        except Exception, e:
            print "getOrderTodayMoney:%s" % e
            return None, None
        

    def setOrderStatus(self, eid, status):
        #'''
        try:
            self.switch()
            return self.red._hset("exec:status", eid, status)
        except Exception, e:
            print e
        #'''

    def getOrderConfigStamp(self):
        try:
            self.switch()
            return self.red._get("exec:timestamp")
        except Exception, e:
            print e
            return 0

    def setUserClickInfo(self, key, field, value):
        tm = 7776000 # 90*24*60*60
        self.red_proxy._hset(key, field, value)
        return self.red_proxy._expire(key, tm)

