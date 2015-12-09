#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from settings import  *
from db.redisdb import RedisDb
from scheduler.log import logerr, dbg, loginfo, logwarn


def pid_file_init(path):
    pid_path = '%s/pid' % path
    pid_file = '%s/logcront.pid' % (pid_path,)
    f = open(pid_file,'w')
    f.write('%u\n' % os.getpid())
    f.close()

if __name__ == '__main__':
    path = os.path.abspath(os.path.dirname(__file__))
    pid_file_init(path)
    red = RedisDb(REDISEVER, REDISPORT)
    while True:
        try:
            time.sleep(60)
            red.cronSetExp()
            
        except Exception, e:
            logerr("CronSetExp:%s" % e)
            continue
