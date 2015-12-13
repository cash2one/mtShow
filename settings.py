#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Copyright 2013 GEO Media iStream Team
    Create by:  Yuanji
    Date: 2013-08-06
'''

"""Global configuration
"""


'''设备ID'''
DEVICE_ID = '03'

LOG_LEVEL = 'INFO'

'''Kafka Server:保存实时统计消息的Broker Server,分区个数5个
    根据分区个数起进程，每个进程负责处理一个分区的数据
'''
T_IMP = "mt-show-v1"
T_CLK = "mt-click-v1"
T_CPA = "test"


MSG_SERVER = ('192.168.1.5',9092)
SENDMSG = True
PART_NUM = 1

MULT_PROCESS_MODEL = False

'''iSHOW服务配置'''
SERVER_PORT = [9901,9904]

'''频次控制接收端口'''
FREQ_PORT = 7800

REDISEVER = (("192.168.1.1",6379),)

'''
    AdExchange info
'''

'''价格解密KEY'''
SOHU_DEC_KEY = 'A98806EBB3B7C77771795B910EE557762BC56FAEBC8F79CC2D39018ED2198299'    #对接 key
AY_E_KEY = 'f74a902be2c33d59d3b5f4067551bff6'
AY_I_KEY = '75e0824408de0c3418af073ecf98556e'
YUKU_DEC_KEY = '9016dcdd08974c498c19c1802e2f332d'
MIZH_DEC_KEY = 'c9a44689755b4f7a96bf61345703e142' #miaozhen
TANX_DEC_KEY = [0xbd,0x5f,0x99,0xfe,0x02,0xd5,0x36,0xdb,0x2d,0xba,0x61,0xd7,0x7d,0x27,0x33,0x53]
GDT_DEC_KEY = 'NjgyMzg1LDE0MzYy'
WEIBO_DEC_KEY = '4040163c95d61c7b8d01bccfb2e15400'


'''AdExchange ID'''
ADX_TANX_ID = 1
ADX_YICH_ID = 2
ADX_MMAX_ID = 3
ADX_SINA_ID = 4
ADX_YUKU_ID = 5
ADX_BES_ID = 6
ADX_TENC_ID = 7
ADX_SOHU_ID = 8
ADX_AMAX_ID = 9
ADX_INMO_ID = 10
ADX_JUXI_ID = 11
ADX_MIZH_ID = 12
ADX_GDT_ID  = 13
ADX_GYIN_ID = 14
ADX_WEIBO_ID = 16


