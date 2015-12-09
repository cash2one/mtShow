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
from Crypto.Cipher import AES

from shdecode import shdecode
from baidecode.baidecode import baidecode
from tedecode.tedecode import tedecode
from jxdecode.jxdecode import jxdecode
from gydecode.gydecode import gydecode
from amdecode import amdecode

print dir(shdecode)

from Crypto.Cipher import AES
from Crypto.Hash import SHA256

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[0:-ord(s[-1])]

def sha1(text):
    s = SHA256.new()
    s.update(text)
    return s.hexdigest()

key = 'c9539dacbe89eec252afa703f28ef06a'
aes = AES.new(key, AES.MODE_ECB)

#text = 'This is some text that will be encrypted'
media = '851_1431483552157'
text = pad(media)
print text
encrypted_text = aes.encrypt(text)
print encrypted_text.encode('hex')

aes = AES.new(key, AES.MODE_ECB)
decrypted_text = aes.decrypt(encrypted_text)
print unpad(decrypted_text)

#print 'Original:\t' + sha1(text)
#print 'Encrypted:\t' + sha1(encrypted_text)
#print 'Decrypted:\t' + sha1(decrypted_text)
