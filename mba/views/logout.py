#!/usr/bin/python
# coding: utf-8

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.security import forget
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user

from mba.resources import MbaUser
from mba import _
from mba.utils import wrap_user


@view_config(route_name='logout' )
def view_logout(request):
    headers = forget(request)
    # request.session.flash(u"成功退出登陆","success")

    return HTTPFound(location="/", headers=headers)


def includeme(config):
    #print 'hear 2'
    settings = config.get_settings()
    config.add_route('logout', '/logout')

    config.scan(__name__)