#!/usr/bin/python
# coding: utf-8

import sys
import datetime
import re
import json
import deform
import colander
import itertools
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.encode import urlencode
from pyramid.response import Response
from js.jquery import jquery
from js.jqueryui import jqueryui
from js.jquery_form import jquery_form
from js.deform import deform_js
from js.jquery_timepicker_addon import timepicker
from js.deform_bootstrap import ui_bootstrap_theme
from mba.fanstatic import mba_form

from kotti import get_settings
from kotti.security import get_principals
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from kotti.security import get_user
from kotti import DBSession

from form import FormCustom
from mba import resources
from mba import _

class PersonInfo(colander.Schema):
    real_name = colander.SchemaNode(
            colander.String(),
            )
    sex = colander.SchemaNode(
            colander.Integer(),
            default=0,
            validator=colander.Range(0, 1),
            )
    birth_date = colander.SchemaNode(
            colander.Date(),
            #'%Y-%m-%d %H:%M:%S'
            default=datetime.datetime.strptime('1990-1-1','%Y-%m-%d').date(),
            )
    identify_type = colander.SchemaNode(
            colander.Integer(),
            validator=colander.Range(0,10)
            )
    identify = colander.SchemaNode(
            colander.String(),
            )
    work_years = colander.SchemaNode(
            colander.Integer(),
            )
    location = colander.SchemaNode(
            colander.String(),
            )
    salary = colander.SchemaNode(
            colander.Integer(),
            )
    email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email()
    )
    phone = colander.SchemaNode(
            colander.String(),
            )
    company_phone = colander.SchemaNode(
            colander.String(),
            )


class Education(colander.MappingSchema):
    name = colander.SchemaNode(
            colander.String(),
            )
    location = colander.SchemaNode(
            colander.String(),
            )
    start_date = colander.SchemaNode(
            colander.Date(),
            )
    finish_date = colander.SchemaNode(
            colander.Date(),
            )
    major = colander.SchemaNode(
            colander.String(),
            )
    degree = colander.SchemaNode(
            colander.String(),
            )
    abroad = colander.SchemaNode(
            colander.Boolean(),
            )
    summary = colander.SchemaNode(
            colander.String(),
            )

def user2person(user):
    person = {}
    if user:
        #user = DBSession.query(resources.Student).get(user.id)
        person['real_name'] = user.real_name or user.name
        if user.birth_date:
            person['birth_date'] = user.birth_date
        person['work_years'] = user.work_years or 0
        person['identify'] = user.identify or ""
        person['identify_type'] = user.identify_type or 0
        person['location'] = user.location or ""
        person['salary'] = user.salary or 1000
        person['email'] = user.email
        person['phone'] = user.phone or ""
        person['company_phone'] = user.company_phone or ""
        person['sex'] = user.sex or 0
    return person

def person2user(user, person):
    user.real_name = person['real_name']
    user.birth_date = person['birth_date']
    user.work_years = person['work_years']
    user.identify = person['identify']
    user.identify_type = person['identify_type']
    user.location = person['location']
    user.salary = person['salary']
    user.phone = person['phone']
    user.company_phone = person['company_phone']
    user.sex = person['sex']

class UserNotFount(Exception):
    pass

@view_config(context=UserNotFount)
def notfount_user_exception(request):
    return HTTPFound(location='/login')

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')

        return json.JSONEncoder.default(self, obj)

@view_config(route_name='resume_edit2', renderer='resume_edit3.jinja2')
def resume_edit2(context, request):
    jquery.need()
    jqueryui.need()
    jquery_form.need()
    #deform_js.need()
    timepicker.need()
    ui_bootstrap_theme.need()
    mba_form.need()

    user = get_user(request)
    if not user:
        raise UserNotFount()

    schema = PersonInfo().bind(request=request)

    if "person_info" in request.POST:
        try:
            person_info = schema.deserialize(request.POST)
            person2user(user, person_info)
            person_info['__result'] = 0
        except colander.Invalid as e:
            # "1" means validate error in serve
            person_info['__result'] = 1
        return Response(json.dumps(person_info, cls=MyEncoder))

    return {
            'person_info':schema.serialize(user2person(user)),
    }

@view_config(route_name='job_view', renderer='job2.jinja2')
def job_view(context, request):
    jquery.need()
    
    user = get_user(request)
    if not user:
        raise UserNotFount()

    return {
            'resumes':user.resumes
            }

def includeme(config):
    settings = config.get_settings()
    config.add_route('resume_edit2','/resume_edit2')
    config.add_route('job_view','/job_view')
    config.scan(__name__)
