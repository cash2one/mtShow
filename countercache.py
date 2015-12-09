#!/usr/bin/env python
# coding=utf-8

import time
import Queue
import threading
from settings import *
from collections import defaultdict
from scheduler.database import Database
from scheduler.log import dbg, loginfo, logwarn, logerr

CACHE_DUR_FREQ = 1
CounterCacheQueue = Queue.Queue()

'''
Queue Info
{   
    'type':1  # 1 pv 2 click 3 cpa ...  
    'adx':xxx,
    'eid':xxx,
    'pid':xxx,
    'aid':xxx,
    'price':xxx
}

Cache info
{
    'pid_info':{
        'exec:impression:pid:eid1':xxx,
        'exec:impression:pid:eid2':xxx,
        'exec:impression:pid:eid3':xxx,
        'exec:exchangeprice:pid:%s':xxx,
    },

    'eid_info':{
        'pv':{'id1':xxxx,'id2':xxx},
        'exchange_price':{'id1':xxx, 'id2':xxx}
    },

    'aid_info':{
        'exchange_price':{'id1':xxx, 'id2':xxx}
    },

    'adx_info':{
        'pv':{'id1':xxx, 'id2':xxx},
        'exchange_price':{'id1':xxx, 'id2':xxx}
    }
}

'''

class CounterCache(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.m_CacheFlag = 1
        self.m_CounterCache = None
        self.m_Cache_A = defaultdict()
        self.m_Cache_B = defaultdict()

        self.database = Database(kafka = False)#Don't Use Kafka Function

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
            for eid in cache['eid_info']['exchange_price'].iterkeys():
                self.database.incEidHourSp(eid, cache['eid_info']['exchange_price'][eid])
                dbg("increase Order:%s Hour Total Cash OK!" % str(eid))
            for eid in cache['eid_info']['pv'].iterkeys():
                self.database.incEidHourPv(eid, cache['eid_info']['pv'][eid])
                dbg("increase Order:%s PV OK!" % str(eid))

        if cache.has_key('aid_info'):
            for aid in cache['aid_info']['exchange_price'].iterkeys():
                self.database.incAdvBidSpend(aid, cache['aid_info']['exchange_price'][aid])
                self.database.decAdvBidSpend(aid, "-%.3f" %  (float(cache['aid_info']['exchange_price'][aid])/1000))

    def run(self):
        while True:
            try:
                time.sleep( CACHE_DUR_FREQ )
                self.chageCacheFlag()
                self.cacheDura()
                self.clearCache()

            except Exception, e:
                logerr(e)
                continue


class threadCounterCachePut(threading.Thread):
    def __init__(self, cache, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.cache = cache
    def run(self):
        while True:
            try:
                info = self.queue.get(block = 1)
                if info:
                    #loginfo(info)
                    self.cache.cacheInfoPut(info)

            except Exception, e:
                logerr(e)
                #print e
                continue

def CounterCacheQueueHandle():
    c_Cache = CounterCache()
    c_Put = threadCounterCachePut( c_Cache, CounterCacheQueue )
    c_Cache.start()
    c_Put.start()
