#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import traceback,json

from settings import  *
from db.kfconnect import KafkaCon
from db.redisdb import RedisDb
from scheduler.log import logerr, dbg, loginfo, logwarn


class Database(object):
    def __init__(self, kafka = True):
        self.kafka_flag = kafka
        self.initDatabase()

    def initDatabase(self):
        if self.kafka_flag:
            self.kfcon = KafkaCon()
        self.red = RedisDb(REDISEVER, REDISPORT)
        self.red_proxy = RedisDb(REDISEVER_PROXY, REDISPORT_PROXY)

    def sendMsgToStat(self, topic, msg):
        return self.kfcon.sendMsgToStat(topic, msg)

    def incEidHourPv(self, eid, num):
        return self.red.incEidHourPv(eid, num)

    def incEidHourCk(self, eid):
        return self.red.incEidHourCk(eid)

    def incEidHourSp(self, eid, num):
        return self.red.incEidHourSp(eid, num)

    def incEidBidSpend(self, eid, num):
        return self.red.incEidBidSp(eid, num)

    def incAdvBidSpend(self, aid, num):
        return self.red.incAdvBidSp(aid, num)

    def decAdvBidSpend(self, aid, num):
        return self.red.decAdvBidSp(aid, num)

    def incPidImpression(self, eid, pid):
        if eid and pid:
            key = "exec:impression:pid:%s" % eid
            return self.red_proxy._hincr(key, pid)

    def incPidClick(self, eid, pid):
        if eid and pid:
            key = "exec:click:pid:%s" % eid
            return self.red_proxy._hincr(key, pid)

    def incPidExPrice(self, eid, pid, price):
        if eid and pid and price:
            key = "exec:exchangeprice:pid:%s" % eid
            return self.red_proxy._hincrby(key, pid, price)

    def incPidArri(self, eid, pid):
        if eid and pid:
            key = "exec:cpa_1:pid:%s" % eid
            return self.red_proxy._hincr(key, pid)

    def incPidReg(self, eid, pid):
        if eid and pid:
            key = "exec:cpa_2:pid:%s" % eid
            return self.red_proxy._hincr(key, pid)

    def setUserClickInfo(self, key, field, value):
        tm = 7776000 # 90*24*60*60
        self.red_proxy._hset(key, field, value)
        return self.red_proxy._expire(key, tm)

    def getUserClickInfo(self, key):
        return self.red_proxy._hgetall(key)

    def setUserArriInfo(self, key, value):
        tm = 86400 # 1*24*60*60
        self.red_proxy._set(key, value)
        return self.red_proxy._expire(key, tm)

    def getUserArriInfo(self, key):
        return self.red_proxy._get(key)
