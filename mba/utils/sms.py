#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'sunset'
__date__ = '20141111'

import datetime
import random
import urllib2
import urllib
import json
from mba.utils import RetDict
from mba.security import DBSession
from mba.resources import ValidationSms


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





def sendsmscore(phonenum, code):




    o = GuanXin()
    try:
        res = o.sendsms(phonenum, code)
    except Exception,ex:
        res = {'success': False, 'errors': "%s" % ex }

    if res['success'] is True:
        return RetDict(retval=u"发送成功")
    else:
        return RetDict(errmsg=res['errors'])




def sendsms(request, phonenum):

    def generate_random_code():
        return str(random.randint(1000,9999) )

    # TO protect the server from SMS attack,
    now = datetime.datetime.now(tz=None)

    # 如果该IP在过去30min内尝试10次以上发送SMS， 封禁此IP
    ip =  request.remote_addr
    ips = DBSession.query(ValidationSms).filter_by(ip=ip).order_by(ValidationSms.id).all()

    if len(ips) >= 10 and ( now - ips[9].send_datetime).seconds < 30 * 60:
        return RetDict(errmsg=u"请务非法操作!")



    smss = DBSession.query(ValidationSms).filter_by(phonenum=phonenum).order_by(ValidationSms.id).all()




    if len(smss) != 0:
        # TODO: this should be configurable
        if len(smss) >= 20:
            return RetDict(errmsg=u"该手机号尝试注册超过20次,永远封禁!")


        last_send_time = smss[0].send_datetime


        if (now - last_send_time).seconds < 60 : # 距上次发送间隔小于60秒
            return RetDict(errmsg=u"这样灌水也是挺累的,请歇息一会儿吧")

        sended_in_24hour = 0
        for sms in smss:
            if (now - sms.send_datetime).seconds <= 24*60*60: # less then One day
                sended_in_24hour += 1
            else:
                break

        if sended_in_24hour >= 5:
            return RetDict(errmsg=u"过去24小时累计发送超过5次,请休息一会儿吧")



    # No record: send sms
    code = generate_random_code()

    # To deploy
    result = sendsmscore(phonenum=phonenum, code=code)

    # for test purpose only below
    # result = RetDict(retval={'istest':True,'code':code})


    if result['errcode'] == result['SUCCESS']:
        # Send ok, write to the DB
        rsms = ValidationSms(phonenum=phonenum, validate_code=code, ip=ip)
        DBSession.add(rsms)

        request.session['sms_validate_code'] = code
        # TODO: setup pyramid-beaker to expire the validate_code in 5 miniutes(more or less)

    return result

