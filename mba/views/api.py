#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'sunset'
__date__ = '20141111'

import random
import datetime

from pyramid.view import view_config

from kotti import  DBSession
from kotti.security import get_user

from mba.resources import Interest, RegisterSms,  MbaUser, Message
from mba.utils import RetDict
from mba.utils.sms import sendsms

@view_config(route_name='ajax_interests', renderer='json', xhr=True)
def ajax_interests(request):

    all = DBSession.query(Interest).all()
    retval = [i.name for i in all ]

    return RetDict(retval=retval)

@view_config(route_name='ajax_sms', renderer='json', xhr=True)
def ajax_sms(request):


    phone = request.POST.get('phone', None)
    type = request.POST.get('type', None) # TYPE 0: register sms

    if len(phone) != 11:
        return RetDict(errmsg=u"手机号码不合法")



    if type == "0":

        def generate_random_code():
            return random.randint(1000,9999)

        # TO protect the server from SMS attack,
        smss = DBSession.query(RegisterSms).filter_by(phonenum=phone).order_by(RegisterSms.id).all()


        if len(smss) != 0:
            if len(smss) >= 20:
                return RetDict(errmsg=u"该手机号尝试注册超过20次,永远封禁!")

            now = datetime.datetime.now(tz=None)
            last_send_time = smss[0].send_datetime
            if now - last_send_time < 60 : # 距上次发送间隔小于60秒
                return RetDict(errmsg=u"这样灌水也是挺累的,请歇息一会儿吧")

            sended_in_24hour = 0
            for sms in smss:
                if now - sms.send_datetime <= 24*60*60: # less then One day
                    sended_in_24hour += 1
                else:
                    break

            if sended_in_24hour >= 5:
                return RetDict(errmsg=u"过去24小时累计发送超过5次,请休息一会儿吧")



        # No record: send sms
        code = generate_random_code()
        result = sendsms(phonenum=phone, code=code)

        if result['errcode'] == result['SUCCESS']:
            # Send ok, write to the DB
            rsms = RegisterSms(phonenum=phone, validate_code=code)
            DBSession.add(rsms)

        return result


    return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)





@view_config(route_name='ajax_private_msg', renderer='json', xhr=True)
def ajax_private_msg(request):

    ret = None

    user = get_user(request)
    if not user:
        return RetDict(errcode=RetDict.ERR_CODE_NOT_LOGIN)


    method = request.POST.get("method", None)
    if not method and method != 'send_private_msg':
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    person_id = request.POST.get("target_person_id", 0)
    if person_id  == 0:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


    person = DBSession.query(MbaUser).filter_by(id=person_id).first()
    if not person:
        return RetDict(errcode=RetDict.ERR_CODE_NO_SUCH_PERSON)


    content = request.POST.get('content', '')

    try:

        message = Message(sender_id=user.id,
                          reciever_id=person_id,
                          type=2,
                          content=content) # TODO: 这里存在SQL注入风险吗?

        DBSession.add(message)
        DBSession.flush()

        ret = RetDict(retval="OK")

    except Exception, ex:
        ret = RetDict(errmsg="%s" % ex)

    finally:
        return ret






def includeme(config):
    config.add_route('ajax_interests','/api/interests.json')
    config.add_route('ajax_sms','/api/sendsms')
    config.add_route('ajax_private_msg','/api/private_msg')
    config.scan(__name__)