#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Yuanji
# Date Time: 2015-08-07 15:36:00
#
###############################################################################
import hmac
import socket
import base64
from settings import *
from Crypto.Cipher import AES
import urllib
import hashlib
import binascii
from binascii import unhexlify, hexlify
from struct import *
from utils.general import *


from baidecode.baidecode import baidecode
from jxdecode.jxdecode import jxdecode

import logging
logger = logging.getLogger(__name__)

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

class PriceSuper:
    def parsePrice(self,en_msg):
        return 0

class PriceNormal(PriceSuper):
    def parsePrice(self,en_msg):
        return int(float(en_msg))


class PriceBaidu(PriceSuper):
    def __init__(self,key=None):

        self.dec = baidecode
        self.dec_key = key
    def parsePrice(self, en_msg):
        try:
            self.real_price = self.dec(en_msg)
            return self.real_price
        except Exception, e:
            print('BaiLogShowHandler/parsePrice: %s'%e)
            return False

class PriceJux(PriceSuper):
    def __init__(self,key=None):

        self.dec = jxdecode
        self.dec_key = key
    def parsePrice(self, en_msg):
        try:
            self.real_price = self.dec(en_msg.replace(" ","+"))
            return int(self.real_price)/10000
        except Exception, e:
            print('JuxLogShowHandler/parsePrice: %s'%e)
            return False

IS_BIG_ENDIAN = True  if socket.htons(1) == 1 else False
class PriceTanx(PriceSuper):
    def __init__(self):
        self.key = [0x01,0xd5,0xba,0xaf,0x00,0x9c,0x4d,0xd6,0xbb,0x01,0xb7,0x11,0xfc,0x74,0x92,0x92]

    def parsePrice(self, bid_result):
        try:
            bid_result = bid_result.replace('-','%')
            src = base64.b64decode(urllib.unquote(bid_result.replace(" ","+")))
            if len(src) != 25:
                return False
            version = src[0]
            bid = src[1:17]
            self.real_bid = toHex(bid)
            pri = src[17:21]
            crc = src[21:25]
            key = ''
            for x in self.key:
                key += chr(int(x))

            md5ob = hashlib.md5(bid+key).digest()
            h4 = md5ob[0:4]
            h4_str = toHex(h4)
            pri_str = toHex(pri)

            real_pri = 0

            p_tmp = ''
            if not IS_BIG_ENDIAN:
                for i in xrange(4):
                    tmp = int(h4_str[i*2:i*2+2],16) ^ int(pri_str[i*2:i*2+2],16)
                    t =  hex(tmp).strip('0x')
                    if len(t) == 1:
                        t = '\0' if not t else binascii.a2b_hex('0'+t)
                    else:
                        t = '\0' if not t else binascii.a2b_hex(t)
                    p_tmp += t
                    real_pri = real_pri | (tmp << i*8)
            else:
                for i in xrange(4):
                    tmp = int(h4_str[i*2:i*2+2],16) ^ int(pri_str[i*2:i*2+2],16)
                    t =  hex(tmp).strip('0x')
                    if len(t) == 1:
                        t = '\0' if not t else binascii.a2b_hex('0'+t)
                    else:
                        t = '\0' if not t else binascii.a2b_hex(t)
                    p_tmp += t
                    real_pri = real_pri | (tmp << (24 - i*8))

            crc_tmp = hashlib.md5(version + bid + p_tmp + key).digest()
            if crc_tmp[0:4] == crc:
                result = True
            else:
                result = False

            #self.real_price = real_pri
            self.real_price = 0 if real_pri > 100000 else real_pri

            return self.real_price
        except Exception, e:
            logger.warn('PriceTanx/parsePrice Error! %s en_msg:%s' % (e,bid_result) )
            self.real_price = 0
            return False

class PriceYouku(PriceSuper):
    def __init__(self,key=None):
        self.key = 'e48c06fe0da2403db2de26e2fcfe14d5' #YKTOKEN

    def hexChar2int(self, oc):
        c = ord(oc)
        if c >= ord('0') and c <= ord('9'):
            i = c - ord('0')
            return i
        elif c >= ord('a') and c <= ord('f'):
            i = c - ord('a') + 10
            return i
        elif c >= ord('A') and c <= ord('F'):
            i = c - ord('A') + 10
            return i
        else:
            return -2;

    def hex2array(self, hex):
        result = ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']
        strlen = len(hex)
        if(32 != strlen):
            return []
        myrange = [0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30]
        for i in myrange:
            tmp_a = self.hexChar2int(hex[i])
            tmp_b = self.hexChar2int(hex[i + 1])
            if (-2 == tmp_a) or (-2 == tmp_b):
                return []
            result[i/2] = chr((tmp_a << 4) + tmp_b)
        return result

    def dec(self, en_msg):
        listkey = self.hex2array(self.key)
        key = ''.join(listkey)
        obj = AES.new(key, AES.MODE_ECB)
        mod4 = len(en_msg) % 4
        if mod4:
            en_msg += ((4 - mod4) * '=')
            pass
        msg = base64.urlsafe_b64decode(en_msg)
        msg1 = unpad(obj.decrypt(msg))
        msgs = msg1.split("_")
        return float(msgs[0])


    def parsePrice(self, en_msg):
        try:

            real_pri = self.dec(str(en_msg))
            if real_pri:
                self.real_price = int(real_pri)

            logger.debug("price: %d" % self.real_price)
            return self.real_price

        except Exception, e:
            logger.error('PriceYouku/parsePrice: %s %s'% (e, en_msg))
            return False

class AdxPriceParser:
    def __init__(self):
        self.strategy = dict()
        try:
            self.strategy[0] = PriceNormal()
            self.strategy[ADX_BES_ID] = PriceBaidu()
            self.strategy[ADX_JUXI_ID] = PriceJux()
            self.strategy[ADX_TANX_ID] = PriceTanx()
            self.strategy[ADX_YUKU_ID] = PriceYouku()
        except Exception,e:
            print "AdxPriceParser:%r" % e

    def parsePrice(self,adx_id, en_msg):
        if self.strategy.has_key(adx_id):
            return self.strategy[adx_id].parsePrice(en_msg)
        else:
            print "No Adx:%s In PriceParser!" % adx_id
            return 0
