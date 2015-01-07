#!/usr/bin/python
# coding: utf-8

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, HiddenWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email
from pyramid.request import Response

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user
from kotti.views.form import AddFormView, EditFormView


from mba import _
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import Banner, Participate
from mba.views.widget import ImageUploadWidget2

from js import fineuploader
from js.jquery import jquery


from mba.utils import RetDict

__author__ = 'sunset'
__date__ = '20150105'
__desc__ = u'认证相关'




@view_config(route_name="i_authentications", renderer='/i/authentications.jinja2')
@wrap_user
def i_authentications(request):
    user = get_user(request)
    if not user :
        return HTTPFound('/login?came_from=%s' % request.url)


    if 'auth_type' in request.POST:
        auth_type = request.POST.get('auth_type')
        if auth_type == 'auth_expert':
            user.auth_expert = user.AUTH_STATUS_REQ_FOR_AUTH
        elif auth_type == 'auth_info':
            user.auth_info = user.AUTH_STATUS_REQ_FOR_AUTH



    authentications = [
        (   'auth_info', u'资料认证', u'管理员确认后即可获得该认证', user.auth_info ),
        (   'auth_meetup', u'活动认证', u'成功参加一次志友汇活动即可获得该认证', user.auth_meetup ),
        (   'auth_friend', u'校友认证', u'与10名校友成功交换名片即可获得该认证', user.auth_friend ),
        (   'auth_honesty', u'诚信认证', u'资料认证、活动认证、校友认证任意两项或以上通过即可获得该认证', user.auth_honesty ),
        (   'auth_expert', u'专家认证', u'管理员确认的专家可获得该认证', user.auth_expert )

    ]


    return {'authentications': authentications}

def includeme(config):


    config.add_route('i_authentications','/i/authentications')
