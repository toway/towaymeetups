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
from kotti import get_settings
from pyramid.httpexceptions import HTTPFound



def wrap_user(func):
    ''' Append a key/value='user':User to the func return value if it is a dict
        Note: put this decorator after @view_config
    '''
    def _wrap_user(document, request):

        user = get_user(request)

        argcount = func.func_code.co_argcount

        if argcount == 1:
            ret_dict = func(request)
        elif argcount == 2:
            ret_dict = func(document, request)

        if isinstance(ret_dict, dict):
            ret_dict.update({'user': user})

        if user :
            if user.status == user.INACTIVE :
                return HTTPFound(location="/register_finish")
            elif user.status == user.TO_FULLFIL_DATA:
                return HTTPFound(location="/register_details")
            elif user.status == user.BANNED:
                return Response("USER BANNED")

        return ret_dict

    return _wrap_user