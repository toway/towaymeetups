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
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email
from pyramid.request import Response

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user

from mba.resources import MbaUser
from mba import _
from mba.utils import wrap_user

__author__ = 'sunset'
__date__ = '20140527'


@view_config(route_name='meetups', header='X-PJAX')
def view_meetups_pjax(request):
    if not get_user(request):
        return HTTPFound("/login")

    if 'X-PJAX' in request.headers:
        print('pjax in')

    return Response("Pjax Meet Ups !")

@view_config(route_name='meetups', renderer='meetups.jinja2')
def view_meetups(request):
   return wrap_user(request, {'project': 'lesson2'})


def includeme(config):
    config.add_route('meetups','/meetups')
    config.scan(__name__)
