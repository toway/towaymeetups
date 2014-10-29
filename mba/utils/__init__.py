#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

from datetime import datetime

import random

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
import kotti
from kotti import get_settings
from kotti.security import get_user

from json import  JSONEncoder


DEFULT_AVATARS_COUNT_COLLETED = 2

def assign_default_avatar(user):

    # assign a random avatar
    # Currently, I only collect 2 default avatars
    avatar_index = int(random.random() * DEFULT_AVATARS_COUNT_COLLETED)
    user.avatar = "%s/default_avatar_%d.png" % (
                                                   get_settings()['mba.avatar_prefix'] ,
                                                   avatar_index)

    return user

def wrap_user(request, ret_dict_to_update):
    user = get_user(request)


    ret_dict_to_update.update({'user':user})

    return ret_dict_to_update



class RetDict(dict):
    SUCCESS = 0

    ERR_CODE_BASE = 8000
    ERR_CODE_NOT_LOGIN      = ERR_CODE_BASE + 1
    ERR_CODE_WRONG_PARAM    = ERR_CODE_BASE + 2


    errcode_to_msg_map = {
        ERR_CODE_NOT_LOGIN      :   u'请先登陆',
        ERR_CODE_WRONG_PARAM    :   u'错误的参数'
    }


    def __init__(self, errcode=0, retval=None, errmsg=""):


        if errmsg and errcode == 0 :
            errcode = self.ERR_CODE_BASE

        if errcode and not errmsg:
            errmsg = self.errcode_to_msg_map.get(errcode, u"未知错误")
        elif errcode and errmsg:
            errmsg = self.errcode_to_msg_map.get(errcode, u"未知错误") + ": " + errmsg

        dict.__init__(self, errcode = errcode,
                         errmsg= errmsg,
                         retval= retval,
                         SUCCESS= self.SUCCESS)




