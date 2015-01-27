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
from mba.fanstatic import resume_edit_js

from kotti import get_settings
from kotti.security import get_principals
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from kotti.security import get_user
from kotti import DBSession

from form import FormCustom
from mba import resources
from mba.utils import wrap_user
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
            validator=colander.Range(0,10),
            default=0,
            )
    identify = colander.SchemaNode(
            colander.String(),
            default="",
            )
    work_years = colander.SchemaNode(
            colander.Integer(),
            default=0,
            )
    city_name = colander.SchemaNode(
            colander.String(),
            default="",
            )
    salary = colander.SchemaNode(
            colander.Integer(),
            default=0,
            )
    email = colander.SchemaNode(
        colander.String(),
        validator=colander.Email()
    )
    phone = colander.SchemaNode(
            colander.String(),
            default="",
            )
    company_phone = colander.SchemaNode(
            colander.String(),
            default="",
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

class JobSchema(colander.Schema):
    id = colander.SchemaNode(
            colander.Integer(),
            )
    resume_id = colander.SchemaNode(
            colander.Integer(),
            )
    industy = colander.SchemaNode(
            colander.String(),
            )
    industy_type = colander.SchemaNode(
            colander.Integer(),
            )
    industy_scale = colander.SchemaNode(
            colander.Integer(),
            )
    duty = colander.SchemaNode(
            colander.String(),
            )
    start_date = colander.SchemaNode(
            colander.Date(),
            )
    finish_date = colander.SchemaNode(
            colander.Date(),
            )
    description = colander.SchemaNode(
            colander.String(), default="",
            )

class ProjectSchema(colander.Schema):
    id = colander.SchemaNode(
            colander.Integer(),
            )
    resume_id = colander.SchemaNode(
            colander.Integer(),
            )
    start_date = colander.SchemaNode(
            colander.Date(),
            )
    finish_date = colander.SchemaNode(
            colander.Date(),
            )
    name = colander.SchemaNode(
            colander.String(),
            )
    tool = colander.SchemaNode(
            colander.String(), default=u"",
            )
    hardware = colander.SchemaNode(
            colander.String(), default=u"",
            )
    software = colander.SchemaNode(
            colander.String(), default=u"",
            )
    description = colander.SchemaNode(
            colander.String(), default=u"",
            )
    duty = colander.SchemaNode(
            colander.String, default=u"",
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
        person['city_name'] = user.city_name or ""
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
    user.city_name = person['city_name']
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

class JobsWidget(object):
    renderer = staticmethod(deform.Form.default_renderer)
    def __init__(self, resume_id, jobs):
        self.resume_id = resume_id
        self.jobs = jobs
        self.template = 'experience_form.jinja2'
    def render(self):
        jobs = []
        for job in self.jobs:
            schema = JobSchema()
            jobs.append(schema.serialize(resources.row2dict(job)))
        return self.renderer(self.template, resume_id=self.resume_id, experience=jobs)

class ProjectWidget(object):
    renderer = staticmethod(deform.Form.default_renderer)
    def __init__(self, resume_id, projects):
        self.resume_id = resume_id
        self.projects = projects
        self.template = 'project_form.jinja2'
    def render(self):
        objs = []
        for obj in self.projects:
            schema = ProjectSchema()
            o = resources.row2dict(obj)
            o['start_date'] = obj.start_date.strftime('%Y-%m-%d')
            o['finish_date'] = obj.finish_date.strftime('%Y-%m-%d')
            objs.append(o)

        return self.renderer(self.template, resume_id=self.resume_id
                , projects = objs)

def cstruct2edu(cstruct, edu):
    edu.start_date = cstruct['start_date']
    edu.finish_date = cstruct['finish_date']
    edu.school_name = cstruct['school_name']
    edu.major = cstruct['major']
    edu.degree = cstruct['degree']

def edit_education(request, user, resume_id):
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
        #flush to get the new id
        DBSession.flush()
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
        edu = DBSession.query(resources.Education).filter_by(resume_id=resume_id, id=int(request.POST['id'])).first()
        oid = edu.id
        DBSession.delete(edu)
        return Response(json.dumps({'__result':0,'id':oid}))
    # raise error, not exists this operation
    return Response(json.dumps({'__result':1}))

def cstruct2job(cstruct, obj):
    obj.industy = cstruct['industy']
    obj.industy_type = cstruct['industy_type']
    obj.industy_scale = cstruct['industy_scale']
    obj.duty = cstruct['duty']
    obj.start_date = cstruct['start_date']
    obj.finish_date = cstruct['finish_date']

def edit_job(request, user, resume_id):
    t = request.POST["experience"]
    if resume_id != int(request.POST['resume_id']):
        #TODO raise error
        pass
    if t == "new":
        resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
        job_schema = JobSchema()
        cstruct = job_schema.deserialize(request.POST)
        job_obj = resources.Job()
        cstruct2job(cstruct, job_obj)
        resume.jobs.append(job_obj)
        #flush to get the new id
        DBSession.flush()
        widget = JobsWidget(resume_id, resume.jobs)
        json_string = json.dumps({'__result':0})
        return Response(json_string+"$"+widget.render())
    elif t == "modify":
        job_schema = JobSchema()
        cstruct = job_schema.deserialize(request.POST)
        DBSession.query(resources.Job).filter_by(resume_id=resume_id, id=int(request.POST['id'])).\
            update(cstruct, synchronize_session=False)
        resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
        widget = JobsWidget(resume_id, resume.jobs)
        json_string = json.dumps({'__result':0})
        return Response(json_string+"$"+widget.render())
    elif t == "delete":
        job = DBSession.query(resources.Job).filter_by(resume_id=resume_id, id=int(request.POST['id'])).first()
        oid = job.id
        DBSession.delete(job)
        return Response(json.dumps({'__result':0,'id':oid}))
    return Response(json.dumps({'__result':1}))

def cstruct2project(cstruct, obj):
    obj.resume_id = cstruct['id']
    obj.start_date = datetime.datetime.strptime(cstruct['start_date'], '%Y-%m-%d')
    obj.finish_date = datetime.datetime.strptime(cstruct['finish_date'], '%Y-%m-%d')
    obj.name = cstruct['name']
    obj.tool = cstruct['tool']
    obj.hardware = cstruct['hardware']
    obj.software = cstruct['software']
    obj.description = cstruct['description']
    obj.duty = cstruct['duty']

def edit_project(request, user, resume_id):
    t = request.POST["project"]
    if resume_id != int(request.POST['resume_id']):
        return Response(json.dumps({'__result':1}))
    #TODO use try/except
    if t == "new":
        resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
        obj = resources.ProjectInfo()
        cstruct2project(request.POST, obj)
        resume.projects.append(obj)
        #flush to get the new id
        DBSession.flush()
        widget = ProjectWidget(resume_id, resume.projects)
        json_string = json.dumps({'__result':0})
        return Response(json_string+"$"+widget.render())
    elif t == "modify":
        cstruct = {}
        cstruct2project(request.POST, cstruct)
        DBSession.query(resources.ProjectInfo).filter_by(resume_id=resume_id, id=int(request.POST['id'])).\
            update(cstruct, synchronize_session=False)
        resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
        widget = ProjectWidget(resume_id, resume.projects)
        json_string = json.dumps({'__result':0})
        return Response(json_string+"$"+widget.render())
    elif t == "delete":
        project = DBSession.query(resources.ProjectInfo).filter_by(resume_id=resume_id, id=int(request.POST['id'])).first()
        oid = project.id
        DBSession.delete(project)
        return Response(json.dumps({'__result':0,'id':oid}))
    return Response(json.dumps({'__result':1}))

@view_config(route_name='resume_edit2', renderer='resume_edit3.jinja2')
def resume_edit2(context, request):
    jquery.need()
    jqueryui.need()
    jquery_form.need()
    #deform_js.need()
    timepicker.need()
    ui_bootstrap_theme.need()
    resume_edit_js.need()

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
            print e
            # "1" means validate error in serve
            person_info = {}
            person_info['__result'] = 1
        return Response(json.dumps(person_info, cls=MyEncoder))
    elif "education" in request.POST:
        return edit_education(request, user, resume_id)
    elif "experience" in request.POST:
        return edit_job(request, user, resume_id)
    elif "project" in request.POST:
        return edit_project(request, user, resume_id)

    resume = DBSession.query(resources.Resume).filter_by(user=user, id=resume_id).first()
    return wrap_user(request,{
            'resume_id':resume_id,
            'person_info':person_schema.serialize(user2person(user)),
            'edu':EducationsWidget(resume_id, resume.educations),
            'exp':JobsWidget(resume_id, resume.jobs),
            'prj': ProjectWidget(resume_id, resume.projects),
    })

#TODO
#@view_config(route_name='resume_view', renderer='job2.jinja2')
def resume_view(context, request):
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
    elif "operator" in request.POST:
        ops = request.POST['operator']
        print ops
        if ops == 'del_resume':
            id = request.POST['operator_id']
            resume = DBSession.query(resources.Resume).get(id)
            if resume and resume.user_id == user.id:
                DBSession.delete(resume)

    return wrap_user(request,{
            'resumes':user.resumes,
            'pcs':user.position_items,
            })


@view_config(route_name='resume_preview',renderer='resume_preview.jinja2')
def resume_preview(context, request):
    user = get_user(request)
    resume = user.resume
    person = user2person(user)
    if user.sex > 0:
        person['sex'] = u'男'
    else:
        person['sex'] = u'女'
    d = datetime.datetime.now()
    if user.birth_date:
        dc = d.year - user.birth_date.year
        if dc < 0:
            dc = 0
        person['birth_count'] = dc
    lastest_job = DBSession.query(resources.Job).filter_by(resume_id=resume.id).order_by(resources.Job.finish_date.desc()).first()
    jobs = DBSession.query(resources.Job).filter_by(resume_id=resume.id).order_by(resources.Job.finish_date.desc()).all()

    return wrap_user(request,{
            'user': user, 
            'user_dict': person,
            'resume':user.resume,
            'last_job': lastest_job,
            'jobs': jobs,
            })
    

def includeme(config):
    settings = config.get_settings()
    config.add_route('resume_edit2','/resume_edit2/{id:\d+}')
    config.add_route('resume_preview', 'resume-preview')
    config.scan(__name__)
