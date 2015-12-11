#!/usr/bin/env python

import json
import socket
import requests
from tornado import gen
from settings import DISTRIBUTOR_SERVER
from settings import DISTRIBUTOR_TIME
from settings import AD_CORE_SERVER
from utils.general import SOCK
from requests.exceptions import *

import logging
logger = logging.getLogger(__name__)

ADSERVER = AD_CORE_SERVER

def resultparser(dic, res):
    res_dic = json.loads(res)
    if dic.has_key('rid') and res_dic.has_key('rid'):
        if dic['rid'] == res_dic['rid']:
            pass
        else:
            print "RequestID check Error!"
            return None
    else:
        pass
    #print res_dic
    return res_dic

class Requester():
    def __init__(self):
      self.session = requests.Session()

    @gen.coroutine
    def getAdReturn(self, dic):
        try:
            #print dic
            res = self.session.post(ADSERVER, json = dic, timeout = float(DISTRIBUTOR_TIME)/1000)
            #print dir(res)
            raise gen.Return()
        except gen.Return as res_info:
            if res.status_code == requests.codes.ok:
                logger.debug(res.content)
                return resultparser(dic, res.content)
            elif res.status_code == requests.codes.no_content:
                logger.info('No Content.Empty Response...')
            else:
                logger.error('Error Response Code: %s' % str(res.status_code))
        except requests.exceptions.ConnectTimeout:
            logger.warn('getAdReturn ConnectTimeout!')
        except requests.exceptions.Timeout:
            logger.warn('getAdReturn Timeout!')
        except Exception, e:
            logger.error('getAdReturn:%s' % e)

class Distributor():
    def __init__(self):
        self.m_server_list = DISTRIBUTOR_SERVER
        self.m_len = len(self.m_server_list)
        self.counter = 0
        if self.m_len == 0:
            print "No DISTRIBUTOR_SERVER In Settings!"

    def _get(self):
        if self.m_len == 0:
            return None
        if self.counter < self.m_len:
            pass
        else:
            self.counter = 0
        return self.m_server_list[self.counter]


    @gen.coroutine
    def dist(self, dic):
        try:
        #if 1:
            dis_server = self._get()
            if dis_server is None:
                return
            else:
                try:
                    s = SOCK()
                    s.settimeout(float(DISTRIBUTOR_TIME)/1000)
                    s.sendto( json.dumps(dic), dis_server)
                    self.counter = self.counter + 1
                    re = s.recvfrom(1024)
                    raise gen.Return()
                except gen.Return as res_info:
                    s.close()
                    return resultparser(dic, re[0])# info
                except socket.timeout:
                    s.close()
                    print 'timeout:%s' % str(dis_server)
                    return None
                    # record
                except Exception, e:
                    s.close()
                    print e
                    return None
        except Exception, e:
            print "Dist Err:%s" % e
            return None

