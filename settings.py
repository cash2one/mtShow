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


MSG_SERVER = ('192.168.2.51',9092)
SENDMSG = True
PART_NUM = 1

MULT_PROCESS_MODEL = False

'''iSHOW服务配置'''
SERVER_PORT = [9901,9908]

'''频次控制接收端口'''
FREQ_PORT = 7800

CONFIG_REDISEVER = (("08dce178449f48fb.m.cnbja.kvstore.aliyuncs.com",6379),)
REDISEVER = (("08dce178449f48fb.m.cnbja.kvstore.aliyuncs.com",6379),)
STATUS_REDIS_PASS = "08dce178449f48fb:MtqweBNM789"



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

