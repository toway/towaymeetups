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
from pyramid.renderers import render_to_response
from pyramid.security import remember
from pyramid.encode import urlencode
from formencode.validators import Email

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user

from mba.resources import Infomation, Banner
from mba import _
from mba.utils.decorators import wrap_user
from mba.views.meetups import query_meetups
from mba.views.person import persons_maybe_know

__author__ = 'sunset'
__date__ = '20140525'

def query_info(request):
     result = DBSession.query(Infomation).limit(20)
     info = [ {'name': it.name,
             'title': it.title,
             'time': it.modification_date}
              for it in result ]

     return {'infomation': info}


def query_banners(request):
    result = DBSession.query(Banner).limit(20)

    return {'banners': result}


@view_config(route_name='home', renderer='home.jinja2')
@wrap_user
def view_home(context, request):
    user = get_user(request)
    if not user:
        return HTTPFound("/login")
    d = query_meetups(request)
    d.update(query_info(request))
    d.update(query_banners(request))
    d.update(persons_maybe_know(user))
    return d


def includeme(config):
    config.add_route('home','/home')
    config.scan(__name__)
