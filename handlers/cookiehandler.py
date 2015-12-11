#!/usr/bin/env python
#-*- coding:utf-8 -*-

###################################################
#
# Create by:  Yuanji 
# Date Time:  2015-06-24 16:03:00
# Content:   Cookie
#
###################################################

import random, time, os, sys

uc_expires = 5000
ad_expires = 1
DOMAIN = '.mtty.com'

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

Encode = {
        0:['p','m','7','M','A','i','Y'],
        1:['a','F','j','2','v','X','2'],
        2:['K','b','E','E','R','f','L'],
        3:['o','8','1','d','w','S','1'],
        4:['5','G','k','5','u','W','T'],
        5:['Q','0','D','C','N','B','Z'],
        6:['n','H','c','3','3','V','e'],
        7:['J','s','l','t','x','U','x'],
        8:['r','9','6','O','z','h','6'],
        9:['q','4','P','4','y','g','I']
    }

Decode = {
        'p':'0','m':'0','7':'0','M':'0','A':'0','i':'0','Y':'0',
        'a':'1','F':'1','j':'1','2':'1','v':'1','X':'1',
        'K':'2','b':'2','E':'2','R':'2','f':'2','L':'2',
        'o':'3','8':'3','1':'3','d':'3','w':'3','S':'3',
        '5':'4','G':'4','k':'4','u':'4','W':'4','T':'4',
        'Q':'5','0':'5','D':'5','C':'5','N':'5','B':'5','Z':'5',
        'n':'6','H':'6','c':'6','3':'6','V':'6','e':'6',
        'J':'7','s':'7','l':'7','t':'7','x':'7','U':'7',
        'r':'8','9':'8','6':'8','O':'8','z':'8','h':'8',
        'q':'9','P':'9','4':'9','y':'9','g':'9','I':'9'
    }

    
class CookieHanlder():
    def __init__(self):
        import random
        self.server_id = random.randint(1,100)
        self.proj_id = random.randint(1,10)
        self.cookie_base1 = 100
        self.cookie_base2 = 1000
        
    def Encrypt(self, code):
        encode = [ random.choice(Encode[code[i]]) for i in xrange(32)]
        my_encode = ''.join(encode)
        return my_encode
    
    def Decrypt(self, code):
        try:
            decode = [ Decode[code[i]] for i in xrange(32)]
        except Exception, e:
            logerr(e)
            return False,0
        
        return True,decode
    
    def setVerifyCode(self, sn_in):
        sn = [ int(sn_in[i]) for i in xrange(24)]
        
        vv = 0              # sum of sn[0] to sn[23]
        v = 0
        for i in sn[0:8]:
            v += i
        sn.append(v / 10)   # sn[24,25] = sum of sn[0] to sn[7]
        sn.append(v % 10)
        vv += v
    
        v = 0
        for i in sn[8:16]:
            v += i
        sn.append(v / 10)   # sn[26,27] = sum of sn[8] to sn[15]
        sn.append(v % 10)
        vv += v
       
        v = 0
        for i in sn[16:24]:
            v += i
        sn.append(v / 10)   # sn[28,29] = sum of sn[16] to sn[23]
        sn.append(v % 10)
        vv += v
        
        v = vv % 100
        sn.append(v / 10)   # sn[30,31] = sum of sn[24] to sn[29]
        sn.append(v % 10)
        return sn
    
    def checkVerifyCode(self, sn_in):
        try:
            sn = [int(sn_in[i]) for i in xrange(32)]
        except Exception, e:
            logerr(e)
            return False
    
        v = 0
        for i in sn[0:8]:
            v += i
        if (v / 10) != sn[24]:
            return False
        if (v % 10) != sn[25]:
            return False
    
        v = 0
        for i in sn[8:16]:
            v += i
        if (v / 10) != sn[26]:
            return False
        if (v % 10) != sn[27]:
            return False
    
        v = 0
        for i in sn[16:24]:
            v += i
        if (v / 10) != sn[28]:
            return False
        if (v % 10) != sn[29]:
            return False
    
        v = sn[24]*10 + sn[25] + sn[26]*10 + sn[27] + sn[28]*10 + sn[29]
        vv = v % 100
        if (vv / 10) != sn[30]:
            return False
        if (vv % 10) != sn[31]:
            return False

        return True
    def setCookieBase(self):
        self.cookie_base1 += 1
        self.cookie_base2 += 1
        if self.cookie_base1 > 999:
            self.cookie_base1 = 100
        if self.cookie_base2 > 9999:
            self.cookie_base2 = 1000
            
    # Check User's Cookie is valid.
    def checkCookie(self, cookie):
        if len(cookie) != 32:
            return False
        flag,verify_code = self.Decrypt(cookie)
        if not flag:
            return False
        return self.checkVerifyCode(verify_code)
    
    def setCookie(self):
        self.setCookieBase()
        sn = "%05u%03u%02u%04u%010.0f" % (self.server_id,self.cookie_base1,self.proj_id,self.cookie_base2,time.time())
        verify_code = self.setVerifyCode(sn)
        cookie = self.Encrypt(verify_code)
        return cookie
