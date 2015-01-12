#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'sunset'
__date__ = '20141111'

import random
import datetime

from pyramid.view import view_config

from kotti import  DBSession
from kotti.security import get_user

from mba.resources import Interest, ValidationSms,  MbaUser, Message
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
    try:
        type = int(type)
    except ValueError:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


    if len(phone.strip()) != 11:
        return RetDict(errmsg=u"手机号码不合法")


    if type == ValidationSms.TYPE_REGISTER:
        return sendsms(request, phonenum=phone)


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