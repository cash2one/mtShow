#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import redis
from settings import *
from collections import defaultdict
from datetime import datetime
from time import localtime,strftime

"""KEY"""
GT_ST_EATTR = "exec:attr:"
GT_ST_ESHOW = "exec:show:"
GT_ST_ECLCK = "exec:click:"
GT_ST_OEXEC = "ord:exec:"
GT_ST_OWSPN = "ord:willspend:"
GT_ST_OHSPN = "ord:havespend:"
GT_ST_EHSPN = "exec:havespend:"
GT_ST_EHCOS = "exec:hourspend:"
GT_ST_EBCOS = "exec:hourbidcost:"
GT_ST_ERESP = "exec:response:"
GT_RP_ESTAT = "exec:status"
GT_RP_ADVDY = "adv:today:"
GT_RP_ADDAY = "adv:%s:%s"
GT_RP_ADREM = "adv:cash:"

"""FIELD"""
GT_ST_OID = "oid"
GT_ST_ADT = "advstype"
GT_ST_WPH = "willpush"
GT_ST_PHF = "pushflag"
GT_ST_HRS = "hourshare"
GT_ST_HSH = "haveshow"
GT_ST_HCK = "haveclick"
GT_ST_RES = "response"
GT_ST_PLT = "platform"

class RedisDb(object):
    def __init__(self, server, port):
        self.r = redis.StrictRedis(host = server, port = port, db=0)
        self.hour = lambda : str(datetime.now().hour).zfill(2)
        self.day = lambda : strftime("%Y-%m-%d", localtime())

    def _get(self, key):
        return self.r.get(key)

    def _set(self, key, vl):
        return self.r.set(key, vl)
    
    def _incr(self, key):
        return self.r.incr(key)    

    def _incrbyfloat(self, key, num):
        return self.r.incrbyfloat(key, num)

    def _decbyfloat(self, key, num):
        return self.r.incrbyfloat(key, num)

    def _hgetall(self, key):
        return self.r.hgetall(key)

    def _hget(self, key, field):
        return self.r.hget(key, field)
    
    def _hset(self, key, field, value):
        return self.r.hset(key, field, value)

    def _hincr(self, key, field):
        return self.r.hincrby(key, field)

    def _incrby(self, key, num):
        return self.r.incrby(key, int(num))

    def _hincrby(self, key, field, num):
        return self.r.hincrby(key, field, int(num)) 

    def _hincrbyfloat(self, key, field, num):
        return self.r.hincrbyfloat(key, field, float(num)) 

    def _expire(self, key, tm):
        return self.r.expire(key, tm)

    def getOidWSpend(self, oid):
        r = self._get(GT_ST_OWSPN + oid) 
        return 0 if r is None else r

    def getOidHSpend(self, oid):
        r = self._get(GT_ST_OHSPN + oid) 
        return 0 if r is None else r
        
    def getEidInfo(self, eid):
        EID = GT_ST_EATTR + eid
        einfo = defaultdict()       
        r = self._hget(EID, GT_ST_OID)        
        einfo[GT_ST_OID] = 0 if r is None else r
        r = self._hget(EID, GT_ST_ADT)        
        einfo[GT_ST_ADT] = 0 if r is None else r
        r = self._hget(EID, GT_ST_WPH)        
        einfo[GT_ST_WPH] = 0 if r is None else r
        r = self._hget(EID, GT_ST_PHF)        
        einfo[GT_ST_PHF] = 0 if r is None else r
        r = self._hget(EID, GT_ST_HRS)        
        einfo[GT_ST_HRS] = 0 if r is None else r
        r = self._hget(EID, GT_ST_HSH)        
        einfo[GT_ST_HSH] = 0 if r is None else r
        r = self._hget(EID, GT_ST_HCK)        
        einfo[GT_ST_HCK] = 0 if r is None else r
        r = self._hget(EID, GT_ST_RES)        
        einfo[GT_ST_RES] = 0 if r is None else r
        r = self._hget(EID, GT_ST_PLT)        
        einfo[GT_ST_PLT] = 0 if r is None else r

        return einfo
    
    def getEidHourPv(self, eid):
        EID = GT_ST_ESHOW + eid
        hourinfo = self._hgetall(EID)
        return sorted(hourinfo.iteritems(), key = lambda pd:pd[0], reverse = False)

    def getEidHourCk(self, eid):
        EID = GT_ST_ECLCK + eid
        hourinfo = self._hgetall(EID)
        return sorted(hourinfo.iteritems(), key = lambda pd:pd[0], reverse = False)
    
    def getEidHourSp(self, eid):
        EID = GT_ST_EHCOS + eid
        hourinfo = self._hgetall(EID)
        return sorted(hourinfo.iteritems(), key = lambda pd:pd[0], reverse = False)

    def getEidHSpend(self, eid):
        r = self._get(GT_ST_EHSPN + eid) 
        return 0 if r is None else r

    def incEidHourPv(self, eid, num):
        EID = GT_ST_ESHOW + eid
        self._hincrby(EID, self.hour(), num)
        DAY_EID = "exec:show:%s:%s" % (self.day(), eid)
        self._hincrby(DAY_EID, self.hour(), num)

    def incEidHourSp(self, eid, num):
        EID = GT_ST_EHCOS + eid
        self._hincrby(EID, self.hour(), num)
        DAY_EID = "exec:hourspend:%s:%s" % (self.day(), eid)
        self._hincrby(DAY_EID, self.hour(), num)

    def incEidBidSp(self, eid, num):
        EID = GT_ST_EBCOS + eid
        return self._hincrby(EID, self.hour(), num)

    def incEidHourCk(self, eid):
        EID = GT_ST_ECLCK + eid
        self._hincr(EID, self.hour())
        DAY_EID = "exec:click:%s:%s" % (self.day(), eid)
        self._hincr(DAY_EID, self.hour())

    def getOidExec(self, oid):
        OID = GT_ST_OEXEC + oid
        return self.r.sort(OID)

    def incAdvBidSp(self, aid, num):
        AID = GT_RP_ADDAY %  ( self.day(), aid)
        self._incrby(AID, num)
        #AID = GT_RP_ADVDY + aid
        #self._incrby(AID, num)

    def decAdvBidSp(self, aid, num):
        AID = GT_RP_ADREM + aid
        return self._decbyfloat(AID, num)

    def cronSetExp(self):
        now = datetime.now()
        stringtime = "%s-%s-%s 23:59:59" % (now.year, now.month, now.day)
        tm = time.strptime(stringtime, "%Y-%m-%d %H:%M:%S")
        tm = int(time.mktime(tm))
        rkeys = [GT_ST_ESHOW, GT_ST_ECLCK, GT_ST_EHCOS, GT_ST_EBCOS, GT_ST_ERESP, GT_RP_ESTAT, GT_RP_ADVDY]
        for key in rkeys:
            val = self.r.keys(key+'*')
            if val:
                for realkey in val:
                    self.r.expireat(realkey, tm)
        
