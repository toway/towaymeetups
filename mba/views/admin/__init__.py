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
from mba.views.admin.meetup import ActAddForm, ActEditForm
from mba.views.review import ReviewEditForm, ReviewAddForm
from mba.resources import MbaUser, Act, Review
__author__ = 'sunset'
__date__ = '20140614'


    


def includeme(config):

    config.include("mba.views.admin.infomation")
    config.include("mba.views.admin.meetup_types")
    config.include("mba.views.admin.persons")
    config.include("mba.views.admin.banners")
    config.include("mba.views.admin.meetup")
    config.include("mba.views.admin.meetup_particinpate")



    config.include("mba.views.admin.review")
    config.include("mba.views.admin.company_admin")
    config.include("mba.views.admin.position_admin")

    config.scan(__name__)
