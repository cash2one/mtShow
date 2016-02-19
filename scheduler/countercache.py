#!/usr/bin/env python
# coding=utf-8

import time
import threading
from settings import *
from collections import defaultdict
from scheduler.database import Database
from tornado.queues import Queue
from tornado.ioloop import  IOLoop
import tornado.gen

from utils.general import INTER_MSG_SHOW, INTER_MSG_CLICK

import logging
logger = logging.getLogger(__name__)

CACHE_DUR_FREQ = 5


class CounterCache(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.m_queue = Queue()
        self.m_CacheFlag = 1
        self.m_CounterCache = None
        self.m_Cache_A = defaultdict()
        self.m_Cache_B = defaultdict()

        self.database = Database(redis_conf = REDISEVER, password = STATUS_REDIS_PASS)

        self.cacheInit(self.m_Cache_A)
        self.cacheInit(self.m_Cache_B)

    def switchCache(self):
        if self.m_CacheFlag == 1:
            return self.m_Cache_A
        elif self.m_CacheFlag == 2:
            return self.m_Cache_B

    def chageCacheFlag(self):
        if self.m_CacheFlag == 1:
            self.m_CacheFlag = 2
        elif self.m_CacheFlag == 2:
            self.m_CacheFlag = 1
    
    def clearCache(self):
        if self.m_CacheFlag == 1:
            self.m_Cache_B.clear()
            self.cacheInit(self.m_Cache_B)
        elif self.m_CacheFlag == 2:
            self.m_Cache_A.clear()
            self.cacheInit(self.m_Cache_A)

    def cacheInit(self, cache):
        cache['pid_info'] = defaultdict(int)
        cache['eid_info'] = { 'pv':defaultdict(int), 'exchange_price':defaultdict(int) }
        cache['adx_info'] = { 'pv':defaultdict(int), 'exchange_price':defaultdict(int) }
        cache['aid_info'] = { 'exchange_price':defaultdict(int) }

    @tornado.gen.coroutine
    def queueMsgPut(self, msg):
        yield self.m_queue.put(msg)

    @tornado.gen.coroutine
    def queueMsgGet(self):
        while True:
            msg = yield self.m_queue.get()
            #print msg
            logger.info('QueueGet:%r' % msg)
            self.cacheInfoPut(msg)

    def cacheInfoPut(self, info):
        cache = self.switchCache()
        type = eid = pid = aid = price = adx = None
        if info.has_key('type'):
            type = info['type']
        if info.has_key('eid'):
            eid = info['eid']
        if info.has_key('pid'):
            pid = info['pid']
        if info.has_key('price'):
            price = info['price']
        if info.has_key('aid'):
            aid = info['aid']
        #if info.has_key('adx'):
        #    adx = info['adx']
        if type == 1 and eid and (price != None) and aid: # pv
            cache['aid_info']['exchange_price'][aid] = cache['aid_info']['exchange_price'][aid] + price
            cache['eid_info']['pv'][eid] = cache['eid_info']['pv'][eid] + 1
            cache['eid_info']['exchange_price'][eid] = cache['eid_info']['exchange_price'][eid] + price
            #cache['adx_info']['pv'][adx] = cache['adx_info']['pv'][adx] + 1
            #cache['adx_info']['exchange_price'][adx] = cache['adx_info']['exchange_price'][adx] + price
        else:
            return None


    def cacheDura(self):
        cache = None
        if self.m_CacheFlag == 1:
            cache = self.m_Cache_B
        if self.m_CacheFlag == 2:
            cache = self.m_Cache_A

        #loginfo(cache)
        if cache.has_key('pid_info'):
            pass
        if cache.has_key('eid_info'):
            it_p = cache['eid_info']['exchange_price']
            it_m = cache['eid_info']['pv']
            for eid in it_p.iterkeys():
                self.database.incEidHourSp(eid, it_p[eid])
                logger.debug("increase Order:%r Money:%r OK!" % (eid, it_p[eid]))
            for eid in it_m.iterkeys():
                self.database.incEidShow(eid, it_m[eid])
                logger.debug("increase Order:%r PV:%r OK!" % (eid,it_m[eid]))

        if cache.has_key('aid_info'):
            it_a = cache['aid_info']['exchange_price']
            for aid in it_a.iterkeys():
                self.database.incAidHourSp(aid, it_a[aid])
                self.database.decAdvBidSpend(aid, "-%.3f" %  (float(it_a[aid])/1000))
                logger.debug("increase Advertiser:%s Money:%s!" % (aid, str(float(it_a[aid])/1000)) )

    def run(self):
        while True:
            try:
                time.sleep( CACHE_DUR_FREQ )
                self.chageCacheFlag()
                self.cacheDura()
                self.clearCache()

            except Exception, e:
                logger.error(e)
                continue


