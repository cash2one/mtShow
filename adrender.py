#!/usr/bin/env python

import json
from urllib import urlencode
from collections import defaultdict
from jinja2 import Environment, PackageLoader
from utils.general import *

env = Environment(loader=PackageLoader('adrender','templates'))

MONITOR_HOST = "http://click.mtty.com"
#MONITOR_HOST = "http://10.111.32.15:10001"
IMP_MONITOR_PATH = "/mt/show?"
CLICK_MONITOR_PATH = "/mt/click?"
IMP_MONITOR_ERROR = "/s_err.gif?"
CLICK_MONITOR_ERROR = "/c_err.gif?"

import logging
logger = logging.getLogger(__name__)

def generate_imp_url(req_dic, res_dic):
    try:
        para = defaultdict()
        para['eid'] = res_dic['eid'] if res_dic.has_key('eid') else ''
        para['aid'] = res_dic['aid'] if res_dic.has_key('aid') else ''
        para['pid'] = res_dic['pid'] if res_dic.has_key('pid') else ''
        para['cid'] = res_dic['cid'] if res_dic.has_key('cid') else ''
        para['area'] = res_dic['area'] if res_dic.has_key('area') else ''
        para['rid'] = res_dic['rid'] if res_dic.has_key('rid') else ''
        para['t'] = req_dic['t']
        para = urlencode(para)
        return MONITOR_HOST + IMP_MONITOR_PATH + para
    except Exception as e:
        print "generate_imp_url:%s" % e
        return MONITOR_HOST + IMP_MONITOR_ERROR + "info=" + e

def generate_click_url(req_dic, res_dic):
    try:
        para = defaultdict()
        para['eid'] = res_dic['eid'] if res_dic.has_key('eid') else ''
        para['aid'] = res_dic['aid'] if res_dic.has_key('aid') else ''
        para['pid'] = res_dic['pid'] if res_dic.has_key('pid') else ''
        para['cid'] = res_dic['cid'] if res_dic.has_key('cid') else ''
        para['impid'] = res_dic['impid'] if res_dic.has_key('impid') else ''
        para['area'] = res_dic['area'] if res_dic.has_key('area') else ''
        para['rid'] = res_dic['rid'] if res_dic.has_key('rid') else ''
        para['t'] = req_dic['t']
        para['url'] = res_dic['click_url'] if res_dic.has_key('click_url') else ''
        para = urlencode(para)
        return MONITOR_HOST + CLICK_MONITOR_PATH + para
    except Exception as e:
        print "generate_imp_url:%s" % e
        return IMP_MONITOR_HOST + CLICK_MONITOR_ERROR + "info=" + e

def creatAdRender(req_dic, res_dic):
    try:
        materail = defaultdict()
        template = env.get_template("html_0.html")
        materail['m_type'] = res_dic['m_type'] if res_dic.has_key('m_type') else 'img'
        materail['m_url'] = res_dic['m_url'] if res_dic.has_key('m_url') else ''
        #materail['click_url'] = res_dic['click_url'] if res_dic.has_key('click_url') else ''
        materail['click_url'] = generate_click_url(req_dic, res_dic)
        #materail['imp_url'] = res_dic['imp_url'] if res_dic.has_key('imp_url') else ''
        materail['imp_url'] = generate_imp_url(req_dic, res_dic)
        materail['cm_url'] = res_dic['cm_url'] if res_dic.has_key('cm_url') else ''
        materail['monitor_url'] = res_dic['monitor_url'] if res_dic.has_key('monitor_url') else ''
        materail['m_width'] = res_dic['m_width'] if res_dic.has_key('m_width') else ''
        materail['m_height'] = res_dic['m_height'] if res_dic.has_key('m_height') else ''
        html = template.render(materail = materail)
        return html
    except Exception as e:
        print "creatAdRenderError:%s" % e
        return defaultAdRender()


def defaultAdRender():
    try:
        template = env.get_template("html_0.html")
        materail = dict()
        materail['m_type'] = 'flash'
        materail['m_url'] = 'http://material.istreamsche.com/test/300x250.swf'
        materail['click_url'] = 'http://bd.kai-ying.com/dsp8/geo-tanx-yjns.html'
        materail['imp_url'] = 'http://lg.istreamsche.com/1x1.gif'
        materail['cm_url'] = 'http://lg.istreamsche.com/1x1.gif'
        materail['monitor_url'] = 'http://lg.istreamsche.com/1x1.gif'
        materail['m_width'] = '300'
        materail['m_height'] = '250'
        html = template.render(materail = materail)
        return html
    except Exception,e:
        print e
        pass


def creatAdJsonBack(req_dic, res_dic):
    try:
        res_back = defaultdict()
        call = req_dic['callback_id'] if req_dic.has_key('callback_id') else ''
        res_back['pid'] = req_dic['pid'] if req_dic.has_key('pid') else ''
        res_back['width'] = req_dic['ad_w'] if req_dic.has_key('ad_w') else ''
        res_back['height'] = req_dic['ad_h'] if req_dic.has_key('ad_h') else ''
        res_back['impid'] = res_dic['impid'] if res_dic.has_key('impid') else ''
        res_back['planid'] = res_dic['eid'] if res_dic.has_key('eid') else ''
        res_back['creativeid'] = res_dic['cid'] if res_dic.has_key('cid') else ''
        res_back['groupid'] = res_dic['gid'] if res_dic.has_key('gid') else ''

        '''ADD'''
        res_back['ctype'] = '1'
        res_back['adstype'] = '1'
        # ctype 1 
        if res_dic.has_key('m_type') and res_dic['m_type'] == 'img':
            res_back['ctype'] = '1'
        if res_dic.has_key('m_type') and res_dic['m_type'] == 'flash':
            res_back['ctype'] = '2'
        if res_dic.has_key('m_type') and res_dic['m_type'] == 'mv':
            res_back['ctype'] = '3'

        res_back['materials'] = list()
        res_back['materials'].append(res_dic['m_url'] if res_dic.has_key('m_url') else '')
        
        res_back['turls'] = list()
        res_back['turls'].append(res_dic['click_url'] if res_dic.has_key('click_url') else '')
        
        res_back['clickurls'] = list()
        res_back['clickurls'].append( generate_click_url(req_dic, res_dic) )
        
        j_back = "%s(%s)" % (call, str( json.dumps(res_back) ))
        logger.debug(j_back)
        return j_back
    except Exception,e:
        logger.error(e)
        return call


def defaultAdJsonBack():
    return ''



def creatDspAdBack( dic, create_dic ):
    try:
        res_back = defaultdict()
        template = env.get_template("html_1.html")
        res_back['pid'] = dic[PARA_KEY_PID] if dic.has_key(PARA_KEY_PID) else ''
        res_back['width'] = dic[PARA_KEY_WIDTH] if dic.has_key(PARA_KEY_WIDTH) else ''
        res_back['height'] = dic[PARA_KEY_HEIGHT] if dic.has_key(PARA_KEY_HEIGHT) else ''
        #res_back['width'] = '300'
        #res_back['height'] = '250'
        res_back['impid'] = dic[PARA_KEY_RID] if dic.has_key(PARA_KEY_RID) else ''
        res_back['advid'] = dic[PARA_KEY_ADVID] if dic.has_key(PARA_KEY_ADVID) else ''
        res_back['unid'] = dic[PARA_KEY_ADX] if dic.has_key(PARA_KEY_ADX) else ''
        res_back['plid'] = dic[PARA_KEY_EID] if dic.has_key(PARA_KEY_EID) else ''
        res_back['gpid'] = dic[PARA_KEY_EID] if dic.has_key(PARA_KEY_EID) else ''
        res_back['cid'] = dic[PARA_KEY_CID] if dic.has_key(PARA_KEY_CID) else ''
        res_back['arid'] = dic[PARA_KEY_AREA] if dic.has_key(PARA_KEY_AREA) else ''
        res_back['xcurl'] = dic[PARA_KEY_XCURL] if dic.has_key(PARA_KEY_XCURL) else ''
        res_back['logo'] = 'true'
        '''ADD'''
        res_back['ctype'] = '1'
        res_back['adstype'] = '1'
        # ctype 1
        if create_dic.has_key(CRT_KEY_TYPE) and create_dic[CRT_KEY_TYPE] == 'img':
            res_back['ctype'] = '1'
        if create_dic.has_key(CRT_KEY_TYPE) and create_dic[CRT_KEY_TYPE] == 'flash':
            res_back['ctype'] = '2'
        if create_dic.has_key(CRT_KEY_TYPE) and create_dic[CRT_KEY_TYPE] == 'mv':
            res_back['ctype'] = '3'

        ''' monitor url '''
        res_back['tview'] = create_dic[CRT_KEY_MONITOR_URL] if create_dic.has_key(CRT_KEY_MONITOR_URL) else ''

        res_back['mtls'] = list()
        if create_dic.has_key(CRT_KEY_MATERIALS):
            for m in create_dic[CRT_KEY_MATERIALS]:
                materail = defaultdict()
                materail['p0'] = m[CRT_KEY_URL] if m.has_key(CRT_KEY_URL) else ''
                materail['p1'] = m[CRT_KEY_CLICK_URL] if m.has_key(CRT_KEY_CLICK_URL) else ''
                materail['p2'] = '000'
                materail['p3'] = m[CRT_KEY_WIDTH] if m.has_key(CRT_KEY_WIDTH) else ''
                materail['p4'] = m[CRT_KEY_HEIGHT] if m.has_key(CRT_KEY_HEIGHT) else ''
                res_back['width'] = materail['p3']
                res_back['height'] = materail['p4']
                res_back['mtls'].append(materail)
        logger.debug(res_back)
        html = template.render(ad = res_back)
        #j_back = "%s(%s)" % (call, str( json.dumps(res_back) ))
        #j_back = "%s" %  str( json.dumps(res_back) )
        return html
    except Exception, e:
        print e
        pass

