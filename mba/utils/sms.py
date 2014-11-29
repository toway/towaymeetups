#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'sunset'
__date__ = '20141111'

import urllib2
import urllib
from mba.utils import RetDict

class Ihuyi(object):
    # url = 'http://106.ihuyi.cn/webservice/sms.php?method=Submit&account=cf_sunset&password=13701958949&mobile=%s&content=%E6%82%A8%E7%9A%84%E9%AA%8C%E8%AF%81%E7%A0%81%E6%98%AF%EF%BC%9A%d%E3%80%82%E8%AF%B7%E4%B8%8D%E8%A6%81%E6%8A%8A%E9%AA%8C%E8%AF%81%E7%A0%81%E6%B3%84%E9%9C%B2%E7%BB%99%E5%85%B6%E4%BB%96%E4%BA%BA%E3%80%82'

    url = "http://106.ihuyi.cn/webservice/sms.php?"

    param_key = ('method', 'account', 'password', 'mobile','content')
    param_val = ['Submit', 'cf_sunset', '13701958949', None,'您的验证码是：%d。请不要把验证码泄露给其他人。']

    code = ''


def sendsms(phonenum, code):
    ihuyi = Ihuyi()

    encoded = ''
    encoded_arr = []
    for i,k in enumerate(ihuyi.param_key):
        v = ihuyi.param_val[i]
        if k == 'mobile':
            v = phonenum
            encoded_arr.append(k+"="+v)
        elif k == 'content':
            v = v % code
            o = urllib.urlencode({k:v})
            encoded_arr.append(o)
        else:
            encoded_arr.append(k+"="+v)


    encoded = '&'.join(encoded_arr)



    print( ihuyi.url + encoded )

    read = urllib2.urlopen( ihuyi.url + encoded ).read()

    print read

    res = read.split(" ")
    if res[0] != "2":
        return RetDict(errmsg=res[1])

    return RetDict(retval=res[1])


