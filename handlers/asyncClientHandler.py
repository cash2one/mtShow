#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#
# Create by: Yuanji
# Date Time: 2015-11-23 14:00:00
# Content:   async request http server  keep-alive surpport
#
###############################################################################

import tornado
from tornado import gen
#from async_keepalive_httpc.keepalive_client import SimpleKeepAliveHTTPClient
from keepalive_client import SimpleKeepAliveHTTPClient

class AsyncClient():
    def __init__(self):
        self.http_client = list()
        self.remote_server = list()
        self.remote_server.append("http://www.baidu.com/")
        self.remote_server.append("http://www.sou360.com/")
        self.initLoop()

    def initLoop(self):
        #io_loop = tornado.ioloop.IOLoop.instance()
        #self.http_client = SimpleKeepAliveHTTPClient(io_loop)
        for ser in self.remote_server:
            io_loop = tornado.ioloop.IOLoop.instance()
            self.http_client.append(SimpleKeepAliveHTTPClient(io_loop))

    @gen.coroutine
    def getFetch(self):
        try:
            ser_count = 0
            resp = yield self.http_client.fetch("http://www.baidu.com/", method = 'GET',connect_timeout = 0.1)
            #for ser in self.remote_server:
            #if 1:
            #    yield self.http_client[ser_count].fetch("%s" % ser, method = 'GET',connect_timeout = 0.1)
            #	ser_count = ser_count + 1

        except Exception, e:
            print e




