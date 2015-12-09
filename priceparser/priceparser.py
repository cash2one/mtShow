#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Yuanji
# Date Time: 2015-08-07 15:36:00
#
###############################################################################
import socket
import base64
from settings import *
from Crypto.Cipher import AES
from scheduler.log import  dbg, logwarn, logerr
import urllib
import hmac
import binascii
from binascii import unhexlify, hexlify
from struct import *
from general import *

from shdecode import shdecode
from baidecode.baidecode import baidecode
from tedecode.tedecode import tedecode
from jxdecode.jxdecode import jxdecode
from gydecode.gydecode import gydecode
from amdecode import amdecode

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

class PriceSuper:
    def parsePrice(self,en_msg):
        return 0

class PriceNormal(PriceSuper):
    def parsePrice(self,en_msg):
        return int(float(en_msg))

class PriceSohu(PriceSuper):
    def __init__(self,key):
        self.dec = shdecode.Decrypt
        self.ttr = shdecode.Hex2String
        self.dec_key = key
    def parsePrice(self,en_msg):
        try:
            return self.dec(self.ttr(en_msg), self.ttr(self.dec_key))
        except Exception, e:
            logerr('PriceSohu/parsePrice: %s' % e)
            return False

class PriceTenc(PriceSuper):
    def __init__(self,key=None):

        self.dec = tedecode
        self.dec_key = key
    def parsePrice(self,en_msg):
        try:
            dbg(str(en_msg))
            real_pri = self.dec(str(en_msg))
            if real_pri != -1:
                self.real_price = real_pri
            else:
                logerr("PriceTenc fail,org price: %s" % en_msg)
                return False

            dbg("price: %d" % self.real_price)
            return self.real_price

        except Exception, e:
            logerr('PriceTenc/parsePrice: %s'%e)
            return False

class PriceBaidu(PriceSuper):
    def __init__(self,key=None):

        self.dec = baidecode
        self.dec_key = key
    def parsePrice(self, en_msg):
        try:
            self.real_price = self.dec(en_msg)
            return self.real_price
        except Exception, e:
            logerr('BaiLogShowHandler/parsePrice: %s'%e)
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
            logerr('JuxLogShowHandler/parsePrice: %s'%e)
            return False

class PriceGyi(PriceSuper):
    def __init__(self,key=None):

        self.dec = gydecode
        self.dec_key = key
    def parsePrice(self, en_msg):
        try:
            self.real_price = self.dec(en_msg.replace(" ","+"))
            return int(self.real_price)
        except Exception, e:
            logerr('GyinLogShowHandler/parsePrice: %s'%e)
            return False

class PriceAllyes(PriceSuper):
    def __init__(self,key=None):
        self.e_key = AY_E_KEY
        self.i_key = AY_I_KEY

    def dec(self,msg):
        data = urllib.unquote(msg)
        mod4 = len(data) % 4
        if mod4:
            data += ((4 - mod4) * '=')
        data = base64.urlsafe_b64decode(data)
        enc_price = data[0:8]
        signature = data[8:12]
        impression_id = data[12:]
        price_pad = hmac.new(self.e_key,impression_id,digestmod=hashlib.sha1).digest()[:8]
        price = ''.join(map(lambda x, y: chr(ord(x)^ord(y)), enc_price,  price_pad))
        conf_sig = hmac.new(self.i_key, price+impression_id,digestmod=hashlib.sha1).digest()[:4]
        if(conf_sig == signature):
            return float(price)
        else:
            return


    def parsePrice(self, en_msg):
        try:
            if en_msg == "undefined":
                return False
            real_pri = self.dec(str(en_msg))
            if real_pri:
                self.real_price = int(real_pri * 100)

            dbg("price: %d" % self.real_price)
            return self.real_price

        except Exception, e:
            logerr('PriceAllyes/parsePrice: %s ,price:%s'%(e, en_msg))
            return False

class PriceAmax(PriceSuper):
    def __init__(self,key=None):

        self.dec = amdecode.decode

    def parsePrice(self, en_msg):
        try:
            real_pri = self.dec(str(en_msg))
            if real_pri != -1:
                self.real_price = int(real_pri/100)
            else:
                logerr("PriceAmax fail,org price: %s" % en_msg)
                return False

            dbg("price: %d" % self.real_price)
            return self.real_price

        except Exception, e:
            logerr('PriceAmax/parsePrice: %s'%e)
            return False



class PriceYouku(PriceSuper):
    def __init__(self,key=None):
        self.key = key #YKTOKEN

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

            dbg("price: %d" % self.real_price)
            return self.real_price

        except Exception, e:
            logerr('PriceYouku/parsePrice: %s %s'% (e, en_msg))
            return False

IS_BIG_ENDIAN = True  if socket.htons(1) == 1 else False
class PriceTanx(PriceSuper):
    def __init__(self,key=None):
        self.key = key

    def parsePrice(self, bid_result):
        try:
            dbg('Parse  Show  Bid_Result')
            src = base64.b64decode(urllib.unquote(bid_result.replace(" ","+")))
            #dbg( 'lenth:%d' % len(src) )
            if len(src) != 25:
                #dbg(' The length of src_content is error! ')
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
            '''
            dbg( 'src:%s' % toHex(src))
            dbg( "crc:%s" % toHex(crc) )
            dbg( "md5:%s" % toHex(md5ob) )
            dbg( "md5 H4:%s" % h4_str )
            dbg( "price:%s" %  pri_str )
            dbg( 'key:%s' % toHex(key))
            '''
            dbg( "version:%s" % toHex(version) )
            dbg( "bid:%s  len:%d" %  (toHex(bid),len(bid)) )

            real_pri = 0

            p_tmp = ''
            if not IS_BIG_ENDIAN:
                #dbg('Small Endian')
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
                #dbg('Big Endian')
                for i in xrange(4):
                    tmp = int(h4_str[i*2:i*2+2],16) ^ int(pri_str[i*2:i*2+2],16)
                    t =  hex(tmp).strip('0x')
                    if len(t) == 1:
                        t = '\0' if not t else binascii.a2b_hex('0'+t)
                    else:
                        t = '\0' if not t else binascii.a2b_hex(t)
                    p_tmp += t
                    real_pri = real_pri | (tmp << (24 - i*8))

            #p_tmp = hex(real_pri).strip('0x').zfill(4)
            #dbg( 'ready md5:%s' %  str(toHex(version + bid + p_tmp + key)))
            crc_tmp = hashlib.md5(version + bid + p_tmp + key).digest()
            #dbg( 'over md5:%s' % toHex(crc_tmp))
            if crc_tmp[0:4] == crc:
                dbg('Check crc OK!')
                result = True
            else:
                dbg('Check crc Fail!')
                result = False

            dbg( 'price:%d' % real_pri )
            dbg('End-BidResult-Parse')
            self.real_price = 0 if real_pri > 5000 else real_pri

            return self.real_price
        except Exception, e:
            logwarn('PriceTanx/parsePrice Error! %s en_msg:%s' % (e,bid_result) )
            self.real_price = 0
            return False

class PriceInmobi(PriceSuper):
    def __init__(self):
        pass
    def parsePrice(self, price):
        return int(float(price)*100)

class PriceGDT(PriceSuper):
    def __init__(self, key = None):
        self.key = key

    def parsePrice(self,en_msg):
        try:
            base64_decode = base64.urlsafe_b64decode(en_msg)
            obj = AES.new( self.key, AES.MODE_ECB )
            return  int( pad(obj.decrypt(base64_decode))[0:15])
        except Exception,e:
            logerr("GDT Price ParserErr:%s " % e)
            return 0

class PriceWeibo():
    def __init__(self, key = None):
        self.key = key

    def parsePrice(self,en_msg):
        try:
            obj = AES.new(self.key, AES.MODE_ECB)
            msg = obj.decrypt(en_msg.decode('hex'))
            return float(msg.split('_')[0])
        except Exception, e:
            logerr('WeiBo parsePrice Err:%s ' % e)
            return 0

class AdxPriceParser:
    def __init__(self):
        self.strategy = dict()
        try:
            self.strategy[0] = PriceNormal()
            self.strategy[ADX_SOHU_ID] = PriceSohu(SOHU_DEC_KEY)
            self.strategy[ADX_TANX_ID] = PriceTanx(TANX_DEC_KEY)
            self.strategy[ADX_YUKU_ID] = PriceYouku(YUKU_DEC_KEY)
            self.strategy[ADX_AMAX_ID] = PriceAmax()
            self.strategy[ADX_MMAX_ID] = PriceAllyes()
            self.strategy[ADX_BES_ID] = PriceBaidu()
            self.strategy[ADX_TENC_ID] = PriceTenc()
            self.strategy[ADX_SINA_ID] = PriceNormal()
            self.strategy[ADX_YICH_ID] = PriceNormal()
            self.strategy[ADX_INMO_ID] = PriceInmobi()
            self.strategy[ADX_JUXI_ID] = PriceJux()
            self.strategy[ADX_MIZH_ID] = PriceYouku(MIZH_DEC_KEY)
            self.strategy[ADX_GYIN_ID] = PriceGyi()
            self.strategy[ADX_GDT_ID] = PriceGDT(GDT_DEC_KEY)
            self.strategy[ADX_WEIBO_ID] = PriceWeibo(WEIBO_DEC_KEY)
        except Exception,e:
            logerr(e)
            pass
    def parsePrice(self,adx_id, en_msg):
        #print self.strategy
        if self.strategy.has_key(adx_id):
            return self.strategy[adx_id].parsePrice(en_msg)
        else:
            logerr("No Adx:%s In PriceParser!" % adx_id)
            return 0
