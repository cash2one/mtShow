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

import json
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter, BinaryEncoder, BinaryDecoder

from kafka.client import KafkaClient
from kafka.producer import SimpleProducer as Producer
import kafka
#print kafka.__version__
import time
#from random import choice
import settings
import threading,logging
from settings import SENDMSG
from scheduler.log import logerr, loginfo, dbg, logwarn
from settings import *
import hashlib
from partchoice.partchoice import GtAdpLogsMd5

LOG_FILENAME_ACCEPT = 'kafka.log'
LOGLEVEL = logging.ERROR
FORMAT = "%(asctime)s %(levelname)-8s %(message)s"
logging.basicConfig(filename=LOG_FILENAME_ACCEPT, level=LOGLEVEL, format=FORMAT)

writers_schema = avro.schema.parse(open("./utils/click.avsc").read())
click_writer = DatumWriter(writers_schema)
writers_schema = avro.schema.parse(open("./utils/impression.avsc").read())
show_writer = DatumWriter(writers_schema)
writers_schema = avro.schema.parse(open("./utils/dermyn.avsc").read())
action_writer = DatumWriter(writers_schema)
writers_schema = avro.schema.parse(open("./utils/cpaarr.avsc").read())
cpaarr_writer = DatumWriter(writers_schema)
writers_schema = avro.schema.parse(open("./utils/cpaact.avsc").read())
cpaact_writer = DatumWriter(writers_schema)
writers_schema = avro.schema.parse(open("./utils/cpamonitor.avsc").read())
cpa_writer = DatumWriter(writers_schema)
writers_schema = avro.schema.parse(open("./utils/tracking.avsc").read())
col_writer = DatumWriter(writers_schema)


def encode(key):
    try:
        return GtAdpLogsMd5(key, PART_NUM)
        #stri = hashlib.md5(key).hexdigest() #32
        '''
        print stri
        print key
        print int(stri[0:16],16)
        print int(stri[16:],16)
        '''
        #return ( int(stri[0:16],16) + int(stri[16:],16) ) % PART_NUM
    except Exception, e:
        logerr("Error in kfconnect encode:%s" % e)
        return 0

class KafkaCon(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.msg_stat_server  = settings.MSG_STAT_SERVER

        self.part_num = settings.PART_NUM

        if SENDMSG:    
            self.stat_con = KafkaClient(self.msg_stat_server[0] +':' + str(self.msg_stat_server[1])) 
            show_producer = Producer(self.stat_con,  async=True)
            click_producer = Producer(self.stat_con, async=True)
            cpa_producer = Producer(self.stat_con,  async=False)
            col_producer = Producer(self.stat_con,  async=False)
            self.stat = {
                         T_IMP:show_producer,
                         T_CLK:click_producer,
                         T_CPA:cpa_producer,
                         T_COL:col_producer
                        }


            self.writer = {
                         T_IMP:show_writer,
                         T_CLK:click_writer,
                         T_CPA:cpa_writer,
                         T_COL:col_writer
                         }


    def sendMsgToStat(self, topic, content):
        if SENDMSG:
            try:
                if isinstance(content, dict):
                    self.stat[topic].send_messages(topic, json.dumps(content).encode('utf-8'))
                    return True
            except UnicodeDecodeError:
                logerr("UnicodeDecodeError: sendMsgToStat Topic:%s Content:%s " % (topic, content))
            except Exception, e:
                logerr("sendMsgToStat Err: Topic:%s %s " % (topic,e))
        else:
            dbg("Failed SENDMSG switch:%s" % str(SENDMSG))
            return False

    def close(self):
        for s in self.stat_con:
            s.close()

    def run(self):
        pass
