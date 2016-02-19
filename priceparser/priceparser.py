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
        self.key = [0xfa,0xd0,0x35,0xed,0x83,0x54,0x1d,0x01,0x38,0x44,0x29,0x78,0x1a,0x5b,0x0a,0xe9]

    def parsePrice(self, bid_result):
        try:
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

            return self.real_price
        except Exception, e:
            print('PriceTanx/parsePrice Error! %s en_msg:%s' % (e,bid_result) )
            self.real_price = 0
            return False

class AdxPriceParser:
    def __init__(self):
        self.strategy = dict()
        try:
            self.strategy[0] = PriceNormal()
            self.strategy[ADX_BES_ID] = PriceBaidu()
            self.strategy[ADX_JUXI_ID] = PriceJux()
            self.strategy[ADX_TANX_ID] = PriceTanx()
        except Exception,e:
            print "AdxPriceParser:%r" % e

    def parsePrice(self,adx_id, en_msg):
        if self.strategy.has_key(adx_id):
            return self.strategy[adx_id].parsePrice(en_msg)
        else:
            print "No Adx:%s In PriceParser!" % adx_id
            return 0
