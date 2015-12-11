#!/usr/bin/env python
'''
    For Kafka Server Connection
    Date: 2013/08/08 
    Create By: Yuanji
'''

try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO

import kafka
from kafka.client import KafkaClient
from kafka.producer import SimpleProducer as Producer
#print kafka.__version__
import time
import json
import settings
import hashlib

import logging
logger = logging.getLogger(__name__)

class KafkaCon():
    def __init__(self):
        self.msg_stat_server  = settings.MSG_SERVER
        self.part_num = settings.PART_NUM
        self.part_counter = 0
        self._initConnect()

    def _initConnect(self):
        try:
            if settings.SENDMSG:    
                self.stat_con = KafkaClient(self.msg_stat_server[0] +':' + str(self.msg_stat_server[1])) 
                show_producer = Producer(self.stat_con,  async=True)
                click_producer = Producer(self.stat_con, async=True)
                action_producer = Producer(self.stat_con,  async=True)

                self.stat = {
                         settings.T_IMP:show_producer,
                         settings.T_CLK:click_producer,
                         settings.T_ACT:action_producer,
                        }
        except Exception, e:
            logger.error('_initConnect Error:%s' % e)

    def _getPartion(self):
        if self.part_counter < self.part_num:
            pass
        else:
            self.part_counter = 0
        return self.part_counter

    def sendMsgToStat(self, topic, content):
        if settings.SENDMSG:
            try:
                if isinstance(content,dict):
                    #partion = self._getPartion()
                    #self.part_counter = self.part_counter + 1
                    self.stat[topic].send_messages(topic, json.dumps(content).encode('utf-8'))   
                    logger.debug('Send Msg to Kafka %s ok!' % topic)
                    return True

            except kafka.common.FailedPayloadsError:
                logger.warn("FailedPayloadsError")
                self._initConnect()
                self.stat[topic].send_messages(topic, json.dumps(content).encode('utf-8'))

            except kafka.common.ConnectionError:
                logger.warn("ConnectionError")
                self._initConnect()
                self.stat[topic].send_messages(topic, json.dumps(content).encode('utf-8'))

            except kafka.common.KafkaUnavailableError:
                logger.warn("KafkaUnavailableError")
                self._initConnect()
                self.stat[topic].send_messages(topic, json.dumps(content).encode('utf-8'))

            except Exception, e:
                logger.error('Send Msg to Kafka Err:%s' % e)
        else:
            logger.debug('settings.SENDMSG:%r' % settings.SENDMSG)
            return False

    def close(self):
        for s in self.stat_con:
            s.close()

