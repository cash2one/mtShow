#!/usr/bin/env python
#-*- coding:utf-8 -*-

###################################################
#
# Create by:  Yuanji
# Date Time:  2015-08-27 16:00:00
#
###################################################

import random, time, os, sys, socket
from scheduler.log import init_syslog, logimpr, logclick, dbg, logwarn, logerr, _lvl
import settings
import urllib,hmac
import base64
import uuid
import hashlib
import binascii
from copy import deepcopy
from collections import defaultdict
from binascii import unhexlify, hexlify
from settings import *
from struct import *
import json
import datetime
import requests

uc_expires = 5000
ad_expires = 1
RESPONSE_BLANK = """(function(){})();"""
LOG_OK = 'ok'
LOG_FAIL = 'fail'
REAL_IP = 'X-Real-Ip' # Need to config in nginx
REMOTE_IP = 'remote_ip'
REFERER = 'Referer'
USER_AGENT = 'User-Agent'
DOMAIN = '.istreamsche.com'
STATICGIF = 'http://gd.geotmt.com/g.gif'


error_times = 0
former_time = time.time()
limit_time = 10*60.0

USER_CLICK_RECORD = "user:click:%s:aid:%s"
USER_SHOW_RECORD = "user:show:%s:aid:%s"

def partChoice(key):
    return GtAdpLogsMd5(key, PART_NUM)


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


def ParseInfo(info):
    try:
        #dbg(info)
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
        #dbg(log)
        return log

    except Exception, e:
        #logerr('SuperShowHandler/parseInfo:%s' % e)
        logwarn('Parse Info Err:%s' % info)
        return False

def timeIndentify(tm, now):
    # one day
    if int(now) - int(tm) <= 86400:
        return True
    else:
        return False

def getRandomKey(msg):
    if msg and msg.has_key('adx_id') and msg.has_key('req_id'):
        return  str(msg["adx_id"]) + '+' + str(msg["req_id"])
    else:
        return str(uuid.uuid4().hex)

