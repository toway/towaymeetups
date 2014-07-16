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
from mba.utils.decorators import wrap_user
from mba.views.activity import ActAddForm
from mba.resources import Act
__author__ = 'sunset'
__date__ = '20140614'


from js.jquery import jquery


def view_meetup_entry():
    jquery.need()
    
    result = DBSession.query(Act).slice(0,20)
    all = [ {'id': it.id,
                'name': it.name, 
             'title': it.title
             }             
                for it in result ]  
    return {'meetups': all}

@view_config(route_name='admin', renderer='admin/meetups.jinja2')
@wrap_user
def view_admin_home(request):
    return view_meetup_entry()

@view_config(route_name='admin_meetups', renderer='admin/meetups.jinja2')
@wrap_user
def view_meetups(request):     
    return view_meetup_entry()


def view_response_test(request):
    return Response("SB")

def includeme(config):
    config.add_route('admin','/admin')
    config.add_route('admin_meetups','/admin/meetups')
    config.add_route('admin_meetup_add',  '/admin/meetup/add')
    config.add_view(ActAddForm, route_name='admin_meetup_add', renderer="admin/meetup_add.jinja2")

    config.add_route("t1","/admin/t1")
    config.add_route("t2","/admin/t2")

    config.add_view(view_response_test, route_name="t1")
    config.add_view(view_response_test, route_name="t2")


    config.scan(__name__)
