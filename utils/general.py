#!/usr/bin/env python

import socket
from random import Random
from settings import *

'''area'''
DEFAULT_AREA = "0086-ffff-ffff"

''' MSG TYPE '''
INTER_MSG_SHOW = 1
INTER_MSG_CLICK = 2

''' OF FLAG '''
OF_FLAG_HMTL = '0'
OF_FLAG_JSON = '1'

''' cookie '''
DEF_USER_COOKIE = 'm'
DOMAIN = '.mtty.com'
UC_EXPIRES = 5000

''' keys '''
USER_CLICK_RECORD = "user:click:%s:aid:%s"
USER_SHOW_RECORD = "user:show:%s:aid:%s"

RESPONSE_BLANK = """(function(){})();"""
''' header '''
REAL_IP = 'X-Real-Ip' # Need to config in nginx
REMOTE_IP = 'remote_ip'
REFERER = 'Referer'
USER_AGENT = 'User-Agent'

def SOCK():
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #soc.bind((SERVIP,Port))
        return soc
    except socket.error, msg:
        print 'Failed to create socket:%s' % msg 


def random_str(randomlength = 16):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str

def chooseAdxID(path):
    adx = ''
    if ADX_BES in path:
        adx = ADX_BES_ID
    elif ADX_TANX in path:
        adx = ADX_TANX_ID
    elif ADX_SOHU in path:
        adx = ADX_SOHU_ID
    elif ADX_YICH in path:
        adx = ADX_YICH_ID
    elif ADX_MMAX in path:
        adx = ADX_MMAX_ID
    elif ADX_SINA in path:
        adx = ADX_SINA_ID
    elif ADX_YUKU in path:
        adx = ADX_YUKU_ID
    elif ADX_TENC in path:
        adx = ADX_TENC_ID
    elif ADX_AMAX in path:
        adx = ADX_AMAX_ID
    elif ADX_INMO in path:
        adx = ADX_INMO_ID
    elif ADX_JUXI in path:
        adx = ADX_JUXI_ID
    elif ADX_MIZH in path:
        adx = ADX_MIZH_ID
    elif ADX_GYIN in path:
        adx = ADX_GYIN_ID
    elif ADX_GDT in path:
        adx = ADX_GDT_ID
    elif ADX_WEIBO in path:
        adx = ADX_WEIBO_ID
    return adx

