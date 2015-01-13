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
from mba.resources import Banner
from mba.views.widget import ImageUploadWidget2

from js import fineuploader
from js.jquery import jquery


from mba.utils import RetDict

__author__ = 'sunset'
__date__ = '20150113'
__desc__ = u'活动参与者'



@view_config(route_name="admin_meetup_particinpate", renderer='find.jinja2')
@wrap_user
def admin_meetup_particinpate_view(context, request):
    return {}


def includeme(config):


    config.add_route('admin_meetup_particinpate',  '/admin/meetup/particinpate/{id}')

