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

default_date = datetime.datetime.strptime('1990-1-1','%Y-%m-%d').date()
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
            default=default_date,
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


class Education(colander.Schema):
    id = colander.SchemaNode(
            colander.Integer(),
            )
    resume_id = colander.SchemaNode(
            colander.Integer(),
            )
    school_name = colander.SchemaNode(
            colander.String(),
            )
    start_date = colander.SchemaNode(
            colander.Date(),
            default=default_date,
            )
    finish_date = colander.SchemaNode(
            colander.Date(),
            default=default_date,
            )
    major = colander.SchemaNode(
            colander.String(),
            )
    degree = colander.SchemaNode(
            colander.Integer(),
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

class EducationsWidget(object):
    renderer = staticmethod(deform.Form.default_renderer)
    def __init__(self, resume_id, edus):
        self.resume_id = resume_id
        self.edus = edus
        self.template = 'education_form.jinja2'

    def render(self):
        educations = []
        for edu in self.edus:
            schema = Education()
            educations.append(schema.serialize(resources.row2dict(edu)))
        return self.renderer(self.template, resume_id=self.resume_id, educations=educations)

def cstruct2edu(cstruct, edu):
    edu.start_date = cstruct['start_date']
    edu.finish_date = cstruct['finish_date']
    edu.school_name = cstruct['school_name']
    edu.major = cstruct['major']
    edu.degree = cstruct['degree']

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

    resume_id = request.matchdict['id']
    resume_id = int(resume_id)

    person_schema = PersonInfo().bind(request=request)
    if "person_info" in request.POST:
        try:
            person_info = person_schema.deserialize(request.POST)
            person2user(user, person_info)
            person_info['__result'] = 0
        except colander.Invalid as e:
            # "1" means validate error in serve
            person_info['__result'] = 1
        return Response(json.dumps(person_info, cls=MyEncoder))
    elif "education" in request.POST:
        t = request.POST["education"]
        if resume_id != int(request.POST['resume_id']):
            #TODO raise error
            pass

        if t == 'new':
            resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
            edu_schema = Education()
            cstruct = edu_schema.deserialize(request.POST)
            edu_obj = resources.Education()
            cstruct2edu(cstruct, edu_obj)
            resume.educations.append(edu_obj)
            widget = EducationsWidget(resume_id, resume.educations)
            json_string = json.dumps({'__result':0})
            return Response(json_string+"$"+widget.render())
        elif t == 'modify':
            edu_schema = Education()
            cstruct = edu_schema.deserialize(request.POST)
            DBSession.query(resources.Education).filter_by(resume_id=resume_id, id=int(request.POST['id'])).\
                update(cstruct, synchronize_session=False)
            resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
            widget = EducationsWidget(resume_id, resume.educations)
            json_string = json.dumps({'__result':0})
            return Response(json_string+"$"+widget.render())
        elif t == 'delete':
            edu = DBSession.query(resources.Education).filter_by(resume_id=resume.id, id=int(request.POST['id'])).first()
            oid = edu.id
            DBSession.delete(edu)
            return Response(json.dumps({'__result':0,'id':oid}))

    resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
    return {
            'resume_id':resume_id,
            'person_info':person_schema.serialize(user2person(user)),
            'edu':EducationsWidget(resume_id, resume.educations),
    }

@view_config(route_name='job_view', renderer='job2.jinja2')
def job_view(context, request):
    jquery.need()
    
    user = get_user(request)
    if not user:
        raise UserNotFount()

    if "add_resume" in request.POST:
        title = request.POST['resume_title']
        if title.strip() != '':
            resume = resources.Resume(title=title, user=user)
            #DBSession.add(resume)
            #DBSession.flush()
            #return HTTPFound(location='/resume_edit2/%d' % resume.id)

    return {
            'resumes':user.resumes
            }

def includeme(config):
    settings = config.get_settings()
    config.add_route('resume_edit2','/resume_edit2/{id:\d+}')
    config.add_route('job_view','/job')
    config.scan(__name__)
