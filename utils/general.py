#!/usr/bin/env python

import socket
from random import Random
from settings import *

''' template '''
NORMAL_TEM = 0
MRAID_TEM  = 1

'''area'''
DEFAULT_AREA = "0086-ffff-ffff"

''' MSG TYPE '''
INTER_MSG_SHOW = 1
INTER_MSG_CLICK = 2

''' OF FLAG '''
OF_FLAG_JSON = '0'
OF_FLAG_BACK = '1'

''' cookie '''
DEF_USER_COOKIE = 'm'
DOMAIN = '.mtty.com'
UC_EXPIRES = 5000

''' user redis keys '''
USER_CLICK_RECORD = "user:click:%s:aid:%s"
USER_SHOW_RECORD = "user:show:%s:aid:%s"

''' parameter  keys '''
PARA_KEY_USER = 'userid'
PARA_KEY_ADX = 'unionid'
PARA_KEY_EID = 'executeid'
PARA_KEY_CID = 'creativeid'
PARA_KEY_PID = 'pid'
PARA_KEY_AREAID = 'areaid'
PARA_KEY_ADVID = 'advid'
PARA_KEY_RID = 'rid'
PARA_KEY_BID_PRICE = 'bid_price'
PARA_KEY_EX_PRICE = 'exchange_price'
PARA_KEY_WIDTH = 'ad_w'
PARA_KEY_HEIGHT = 'ad_h'
PARA_KEY_AREA = 'areaid'
PARA_KEY_XCURL = 'xcurl'
PARA_KEY_REF = 'referer'
PARA_KEY_SOURCEID = 'click_sourceid'

''' creative keys '''
CRT_KEY_TYPE = "m_type"
CRT_KEY_URL = 'material_url'
CRT_KEY_WIDTH = 'width'
CRT_KEY_HEIGHT = 'height'
CRT_KEY_CLICK_URL = 'click_url'
CRT_KEY_MONITOR_URL = 'monitor_url'
CRT_KEY_MATERIALS = 'materials'

RESPONSE_BLANK = """(function(){})();"""
''' header '''
REAL_IP = 'X-Real-Ip' # Need to config in nginx
REMOTE_IP = 'remote_ip'
REFERER = 'Referer'
USER_AGENT = 'User-Agent'


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

def is_num_by_except(num):
    try:
        int(num)
        return True
    except ValueError:
        return False

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

