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

from js.jquery import jquery
from js.jqueryui import jqueryui

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user

from mba.resources import Infomation, Banner
from mba import _
from mba.utils.decorators import wrap_user
from mba.views.meetups import query_meetups
from mba.views.person import persons_maybe_know
from mba.views.position import query_by_cities

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
    result = DBSession.query(Banner).filter_by(status=Banner.VALID, type=Banner.TYPE_HOME).limit(5)

    return {'home_banners': result}


@view_config(route_name='home', renderer='home.jinja2')
@wrap_user
def view_home(context, request):

    user = get_user(request)
    if not user:
        return HTTPFound("/login")

    jqueryui.need()

    first_available_invitation_code = None
    if len(user.available_invitation_codes)>0:
        first_available_invitation_code = user.available_invitation_codes[0].code

    d = query_meetups(request)
    d.update(query_info(request))
    d.update(query_banners(request))
    d.update(persons_maybe_know(user))
    d.update({'application_url': request.application_url})
    d.update({'all_pos': query_by_cities()})
    d.update({'first_available_invitation_code': first_available_invitation_code})
    return d


def includeme(config):
    config.add_route('home','/home')
    config.scan(__name__)
