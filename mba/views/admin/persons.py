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


from mba import _
from mba.utils.decorators import wrap_user
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import MbaUser, Student

__author__ = 'sunset'
__date__ = '20140909'
__description__ = u'用户管理'


from js.jquery import jquery



def view_persons(page_index=1, num_per_page=10):
    jquery.need()

    start = (page_index-1) * num_per_page

    count = DBSession.query(MbaUser).count()
    persons = DBSession.query(MbaUser).slice(start, num_per_page).all()

    return {
        'persons': persons,
        'total_count': count,
        'total_page': count/ num_per_page + 1,
        'page_index': page_index
    }

def view_persons_by_auth(page_index=1, num_per_page=10, authed=0):
    jquery.need()

    start = (page_index-1) * num_per_page

    count = DBSession.query(Student).filter_by(auth_info=authed).count()
    persons = DBSession.query(Student).filter_by(auth_info=authed).slice(start, num_per_page).all()


    return {
        'persons': persons,
        'total_count': count,
        'total_page': count/ num_per_page + 1,
        'page_index': page_index
    }


@view_config(route_name='admin_persons', renderer='admin/persons.jinja2',permission='view')
@wrap_user
def view_all_persons(request):
    return view_persons(1, 10)


@view_config(route_name='admin_persons_auth', renderer='admin/persons.jinja2',permission='view')
@wrap_user
def view_persons_auth(request):
    return view_persons_by_auth(1, 10, 0)


def includeme(config):



    config.add_route('admin_persons','/admin/persons')
    config.add_route('admin_persons_auth',  '/admin/persons/unauth')



    config.scan(__name__)
