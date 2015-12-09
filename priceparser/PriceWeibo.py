#!/usr/bin/env python

import base64
from Crypto.Cipher import AES

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

class PriceWeibo():
    def __init__(self, key = None):
        self.key = key

    def parsePrice(self,en_msg):
        try:
            obj = AES.new(self.key, AES.MODE_ECB)
            msg = obj.decrypt(en_msg.decode('hex'))
            return float(msg.split('_')[0])
        except Exception:
            print 'WeiBo parsePrice Err!'
            return 0


if __name__ == '__main__':
    p = PriceWeibo(key = 'c9539dacbe89eec252afa703f28ef06a')
    print p.parsePrice('d117a2c889b728e123e7ac2bb933a29851a0a53d3f8ff70ed604d26538a8585a')
    print p.parsePrice('d117a2c889b728e123e7ac2bb933a2985b6da254840ae7a87b1733b8c94df303')
    
