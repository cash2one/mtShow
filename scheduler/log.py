#!/usr/bin/env python
#
# Copyright 2012 GEOmedia iStream Team
# Create by:  Wu Peng
# Date:       2012-06-24

"""record schedule, impression and click log
"""
import sys
import syslog
from datetime import datetime
import traceback
from settings import LOG_LEVEL

# first one is xxxx_0.log. second one is xxxx_1.log
# for details check syslog.conf of linux
_CLICK_LOG = (syslog.LOG_INFO, syslog.LOG_DEBUG)
_IMPR_LOG = (syslog.LOG_WARNING, syslog.LOG_ALERT)
_SCHD_LOG = (syslog.LOG_CRIT, syslog.LOG_NOTICE)
_COMM_LOG = syslog.LOG_ERR

_LEVEL = ('DEBUG', 'INFO', 'WARN', 'ERROR')

def getLogLvL():
    _lvl = 2  # WARN
    try:
        _lvl = _LEVEL.index(LOG_LEVEL)
    except ValueError:
        pass
    _lvl = _lvl == -1 and 2 or _lvl

    return _lvl

_lvl = getLogLvL()


def init_syslog(log_local=syslog.LOG_LOCAL0):
    # For python 2.6 there is no 'facility' keyword parameter
    syslog.openlog('istream', syslog.LOG_PID,log_local)

def _logit(level, *fields):
    """log into syslog

    'click', 'schd' and 'impress' have two log files 
    with even hour and odd hour.
    """
    sublevel = level[datetime.now().hour % 2] # Which level
    syslog.syslog(sublevel,'\t'+('\t'.join(map(lambda x: str(x), fields))))

def logclick(*fields):
    _logit(_CLICK_LOG, *fields)

def logimpr(*fields):
    _logit(_IMPR_LOG, *fields)

def logschd(*fields):
    _logit(_SCHD_LOG, *fields)

def logwarn(msg=''):
    if (_lvl > _LEVEL.index('WARN')):
        return
    
#    if (_lvl == 0): # debug
#        print '%-10s\t%s' % ('[WARN    ]', msg)

    syslog.syslog(_COMM_LOG, '%-10s\t%s' % ('[WARN    ]', msg))

def logerr(msg=''):
    if (_lvl > _LEVEL.index('ERROR')):
        return
    e = traceback.format_exc()

    if e == 'None\n':
        e = ''
    
#    if (_lvl == 0): # debug
#        print '%-10s\t%s\n%s' % ('[ERROR   ]', msg, e)
    syslog.syslog(_COMM_LOG, '%-10s\t%s\n%s' % ('[ERROR   ]', msg, e))

def loginfo(msg=''):
    if (_lvl > _LEVEL.index('INFO')):
        return

#    if (_lvl == 0): # debug
#        print '%-10s\t%s' % ('[INFO    ]', msg)

    syslog.syslog(_COMM_LOG, '%-10s\t%s' % ('[INFO    ]', msg))

def dbg(msg=''):
    if (_lvl > _LEVEL.index('DEBUG')):
        return

#    print '%-10s\t%s' % ('[DEBUG   ]', msg)
    syslog.syslog(_COMM_LOG, '%-10s\t%s' % ('[DEBUG   ]', msg))

if __name__ == '__main__':
    pass
#    import sys
#    import random, time
#
##    f = [logclick, logimpr, logschd, logcomm]
#    init_syslog()
##
#    while True:
#        if (datetime.now().second == 0):
#            break
#
#    t1 = time.time()
#    for i in range(1000):
#            random.choice(f)('proc %s: syslog %d %s' % ('0', i, 'a'*180))
##
##    print 'proc %s time: %f' %('0', time.time() - t1)
#
#    dbg('this is dbgerr')
