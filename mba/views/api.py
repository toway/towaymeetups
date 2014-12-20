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
        now = datetime.datetime.now(tz=None)

        # 如果该IP在过去30min内尝试10次以上发送SMS， 封禁此IP
        ip =  request.remote_addr
        ips = DBSession.query(RegisterSms).filter_by(ip=ip).order_by(RegisterSms.id).all()

        if len(ips) >= 10 and ( now - ips[9].send_datetime).seconds < 30 * 60:
            return RetDict(errmsg=u"请务非法操作!")



        smss = DBSession.query(RegisterSms).filter_by(phonenum=phone).order_by(RegisterSms.id).all()




        if len(smss) != 0:
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
        # result = sendsms(phonenum=phone, code=code)

        # for test purpose only below
        result = RetDict(retval={'istest':True,'code':code})


        if result['errcode'] == result['SUCCESS']:
            # Send ok, write to the DB
            rsms = RegisterSms(phonenum=phone, validate_code=code, ip=ip)
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



@view_config(route_name='ajax_person', renderer='json', xhr=True)
def ajax_person(request):
    ret = None

    user = get_user(request)
    if not user:
        return RetDict(errcode=RetDict.ERR_CODE_NOT_LOGIN)


    method = request.POST.get("method", None)
    if not method and method not in ['update_privacy_level']:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    try:

        email_privacy_level = request.POST.get("email-privacy-level", 5)
        title_privacy_level = request.POST.get("title-privacy-level", 5)
        phone_privacy_level = request.POST.get("phone-privacy-level", 5)
        company_privacy_level = request.POST.get("company-privacy-level", 9)

        user.email_privacy_level = email_privacy_level
        user.title_privacy_level = title_privacy_level
        user.phone_privacy_level = phone_privacy_level
        user.company_privacy_level = company_privacy_level

        ret = RetDict(retval="OK")

    except Exception,ex:
        ret = RetDict(errmsg="%s" % ex)

    finally:
        return ret





def includeme(config):
    config.add_route('ajax_interests','/api/interests.json')
    config.add_route('ajax_sms','/api/sendsms')
    config.add_route('ajax_private_msg','/api/private_msg')
    config.add_route("ajax_person",'/api/person')
    config.scan(__name__)