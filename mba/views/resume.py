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

class Education(colander.MappingSchema):
    name = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget()
            )
    location = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget()
            )
    start_date = colander.SchemaNode(
            colander.Date(),
            widget = deform.widget.DateInputWidget()
            )
    finish_date = colander.SchemaNode(
            colander.Date(),
            widget = deform.widget.DateInputWidget()
            )
    major = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.CheckboxWidget()
            )
    degree = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.CheckboxWidget()
            )
    abroad = colander.SchemaNode(
            colander.Boolean(),
            widget=deform.widget.CheckboxWidget()
            )
    summary = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget()
            )

class Educations(colander.SequenceSchema):
    education = Education()

class Resume(colander.MappingSchema):
    title = colander.SchemaNode(
            colander.String(),
            title=u'简历名称'
            )
    educations = Educations()

@view_config(route_name='add_resume', renderer='col_test.jinja2')
def add_resume(context, request):
    schema = Resume().bind(request=request)
    form = deform.Form(schema, buttons=('submit',))
    rendered_form = None
    if 'submit' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()
        else:
            print appstruct
    if rendered_form is None:
        rendered_form = form.render(request.params)
    return {'form': jinja2.Markup(rendered_form)}

def choice_empty_widget(**kw):
    widget = deform.widget.CheckboxChoiceWidget(**kw)
    widget.template = 'choice_empty'
    return widget

class PersonInfo(colander.Schema):
    id_types = (
                (-1,u'选择'),
                (0,u'身份证'),
                (1,u'护照'),
                (2,u'警官证')
            )
    sex_choice = (
            (0, u'男'),
            (1, u'女'),
            )
    real_name = colander.SchemaNode(
            colander.String(),
            css_class="form-control input-sm",
            size='20',
            widget = deform.widget.TextInputWidget(category='structural')
            )
    sex = colander.SchemaNode(
            colander.Integer(),
            default=0,
            widget = choice_empty_widget(
                category="structural",
                values=sex_choice)
            )
    birth_date = colander.SchemaNode(
            colander.Date(),
            widget = deform.widget.DateInputWidget(
                css_class="selectpicker inline slt-year",
                category='structural'
                )
            )
    identify_type = colander.SchemaNode(
            colander.Integer(),
            widget = deform.widget.SelectWidget(category='structural', values=id_types)
            )
    identify = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(
                size='20',
                css_class="selectpicker inline slt-year",
                category='structural'
                )
            )
    work_years = colander.SchemaNode(
            colander.Integer(),
            widget = deform.widget.SelectWidget(
                category="structural",
                css_class="form-control selectpicker",
                values=((1,u'小于一年'), 
                    (2,u'一到三年'),
                    (3,u'三年到五年'),
                    (4,u'五年以上'),
                    )
                )
            )
    location = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(
                css_class="selectpicker inline slt-year",
                size="20",
                category='structural'
                )
            )
    salary = colander.SchemaNode(
            colander.Integer(),
            widget = deform.widget.TextInputWidget(
                css_class="form-control inline input-sm input-middle-width",
                category='structural'
                )
            )
    email = colander.SchemaNode(
        colander.String(),
        widget = deform.widget.TextInputWidget(
            category='structural',
            css_class="form-control  input-sm",
            size='20',
        ),
        validator=colander.Email()
    )
    phone = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(
                category='structural',
                css_class='form-control inline input-sm input-middle-width',
                size='22'
                )
            )
    company_phone = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(
                category='structural',
                css_class='form-control inline input-sm input-middle-width',
                size='22'
                )
            )

def user2person(user):
    person = {}
    if user:
        #user = DBSession.query(resources.Student).get(user.id)
        person['real_name'] = user.real_name or user.name
        person['birth_date'] = user.birth_date or '1990-1-1'
        person['work_years'] = user.work_years or 0
        person['identify'] = user.identify or ""
        person['identify_type'] = 0
        person['location'] = user.residence or ""
        person['salary'] = user.salary or 1000
        person['email'] = user.email
        person['phone'] = user.phone or ""
        person['company_phone'] = user.company_phone or ""
        person['sex'] = user.sex or 0
    return person

@view_config(route_name='resume_edit2', renderer='resume_edit2.jinja2')
def resume_edit(context, request):
    jqueryui.need()

    forms = {}
    schema = PersonInfo().bind(request=request)
    #Warning cannot user name attribute!!!
    person_form = FormCustom(schema, 
            template='resume_edit_form', formid='person_form',
            buttons=( deform.form.Button(u'submit',title=u'保存',css_class='btn btn-primary mba-btn-position'),))
    forms['person_form'] = person_form

    rendered_form = None
    if 'submit' in request.POST:
        posted_formid = request.POST['__formid__']
        this_form = forms[posted_formid]
        try:
            controls = request.POST.items()
            results = this_form.validate(controls)
            print results
        except:
            pass
    if rendered_form is None:
        rendered_form = person_form.render(request.params)
    return {
            'person_form': jinja2.Markup(rendered_form)
            }
@view_config(route_name='resume_edit3',
             request_method='GET',
             accept='*/json',
             renderer='json',
             xhr=True)
@view_config(route_name='resume_edit3', renderer='resume_edit3.jinja2')
def resume_edit3(context, request):
    jquery.need()
    jqueryui.need()
    jquery_form.need()
    #deform_js.need()
    timepicker.need()
    ui_bootstrap_theme.need()
    mba_form.need()

    user = get_user(request)
    person_info = user2person(user)

    if "person_info" in request.POST:
        person_info['work_years'] = 1
        return Response(json.dumps(person_info))

    return {
            'person_info':person_info,
    }

def includeme(config):
    settings = config.get_settings()
    config.add_route('add_resume','/add_resume')
    config.add_route('resume_edit2','/resume_edit2')
    config.add_route('resume_edit3','/resume_edit3')
    config.scan(__name__)
