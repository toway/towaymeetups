#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'
__date__ = '20140528'

from datetime import datetime

import random

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
from pyramid.request import Request,Response
import kotti
from kotti.security import get_user

DEFULT_AVATARS_COUNT_COLLETED = 2

def wrap_user(func):
    ''' Append a key/value='user':User to the func return value if it is a dict
        Note: put this decorator after view_config     
    '''
    def _wrap_user(document, request):

        user = get_user(request)
        if user is not None:
            if user.avatar is None:
                # assign a random avatar
                # Currently, I only collect 2 default avatars
                avatar_index = int(random.random() * DEFULT_AVATARS_COUNT_COLLETED)
                user.avatar = "default_avatar_%d.png" % avatar_index
            # end if
        # end if

        varnames = func.func_code.co_varnames[0:func.func_code.co_argcount]
        ret_dict = func(*varnames)
        if isinstance(ret_dict, dict):
            ret_dict.update({'user': user})
        return ret_dict

    return _wrap_user