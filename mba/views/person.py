#!/usr/bin/python
# coding: utf-8


__author__ = 'ycf'


import deform
from deform import Button
from deform import Form
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from deform.widget import HiddenWidget

import colander
import jinja2
from deform import ValidationFailure
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool

from kotti import get_settings
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from mba import _
from mba.utils import wrap_user






@view_config(route_name='person',renderer='person.jinja2')
def view_job(request):
    return wrap_user(request, {
                "test":"test"
                # "info":  {img:"/mba/img/avatar.jpg",name:"戴昊",company:"MBA志友汇-创始人",address:"深圳",job:"互联网\社交网络\人脉管理",telphone:"13458776315",email:"daihao@163.com",school:"四川大学", expertise:"击剑、电脑、维修",
                # hobby:"绘画、骑车、户外、音乐、电影",wanglai:"咖啡厅、图书馆、电影院",introduct:"善良、喜欢各种体育活动",name:"戴昊",name:"戴昊",name:"戴昊",name:"戴昊",name:"戴昊"}
           })


def includeme(config):
    settings = config.get_settings()
    config.add_route('person','/person/{d}')
    config.scan(__name__)
