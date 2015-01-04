#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'sunset'
__date__ = '20141111'

import urllib2
import urllib
import json
from mba.utils import RetDict


class GuanXin(object):

    URL = "http://denglu.guanxinapp.com/send_text.ext"

    CONTENT_TEMPLATE = "您的验证码是：%s。请不要把验证码泄露给其他人。"


    def sendsms(self, phonenum, code):
        req = urllib2.Request(self.URL)
        req.add_header('X-Send-Text','cascade')
        req.add_header('X-Ajax-Header','ajax-post')
        req.add_header('X-Requested-With','XMLHttpRequest')
        req.add_data(urllib.urlencode({'mobile':phonenum,'content': self.CONTENT_TEMPLATE % code}))


        # print req



        res = urllib2.urlopen(req)
        response = res.read()
        resobj = json.loads(response)

        return resobj





def sendsms(phonenum, code):

    o = GuanXin()
    try:
        res = o.sendsms(phonenum, code)
    except Exception,ex:
        res = {'success': False, 'errors': "%s" % ex }

    if res['success'] is True:
        return RetDict(retval=u"发送成功")
    else:
        return RetDict(errmsg=res['errors'])


