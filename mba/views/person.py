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
                "test":"test",
                "resumes":  [{"date": "2013-3-2", "name":u"UI设计师"},{"date": "2013-3-2", "name":u"UI设计师"}]
           })


def includeme(config):
    settings = config.get_settings()
    config.add_route('person','/person/{d}')
    #config.scan(__name__)
