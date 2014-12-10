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
from mba.utils import wrap_user as wrap_user2
from mba.utils.decorators import wrap_user
from kotti.security import get_user
from mba.resources import *


@view_config(route_name='resume_manager', renderer="job2_manage.jinja2")
@wrap_user
def view_job(request):
    resumes = []
    user = get_user(request)
    if not user:
        raise UserNotFount()
    if not user.resume:
        user.resume = Resume(title=u'默认简历')
        DBSession.flush()
    resumes.append(user.resume)

    return {
            'resumes': resumes
            }


def includeme(config):
    settings = config.get_settings()
    config.add_route('resume_manager','/resume-manager')
    config.scan(__name__)
