#!/usr/bin/env python
# coding=utf-8

import json
import time
from settings import *
from collections import defaultdict
from scheduler.database import Database

import logging
logger = logging.getLogger(__name__)


class CreateCache():
    def __init__(self):
        self.database = Database(redis_conf = CONFIG_REDISEVER)

    def getCreateDetail(self, cid):
        try:
            res = self.database.getCreateInfo(cid)
            if not res:
                return None
            else:
                return json.loads(res)
        except Exception,e:
            logger.error(e)

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
        cache['cid'] = defaultdict()



    def cacheInfoPut(self, info):
        cache = self.switchCache()


    def run(self):
        while True:
            try:
                time.sleep( 1 )
                self.chageCacheFlag()
                self.cacheDura()
                self.clearCache()

            except Exception, e:
                logger.error(e)
                continue


