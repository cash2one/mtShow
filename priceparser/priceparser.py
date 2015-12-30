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

class AdxPriceParser:
    def __init__(self):
        self.strategy = dict()
        try:
            self.strategy[0] = PriceNormal()
            self.strategy[ADX_BES_ID] = PriceBaidu()
            self.strategy[ADX_JUXI_ID] = PriceJux()
        except Exception,e:
            print e
            pass
    def parsePrice(self,adx_id, en_msg):
        if self.strategy.has_key(adx_id):
            return self.strategy[adx_id].parsePrice(en_msg)
        else:
            print "No Adx:%s In PriceParser!" % adx_id
            return 0
