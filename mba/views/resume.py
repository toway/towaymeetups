#!/usr/bin/python
# coding: utf-8

import sys
import datetime
import re
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

from kotti import get_settings
from kotti.security import get_principals
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema

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

class PersonInfo(colander.Schema):
    name = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(category='structural')
            )
    birth_date = colander.SchemaNode(
            colander.Date(),
            widget = deform.widget.DateInputWidget(category='structural')
            )
    idenfity_type = colander
    idenfity = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(category='structural')
    location = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(category='structural')
            )
    salary = colander.SchemaNode(
            colander.Integer(),
            widget = deform.widget.TextInputWidget(category='structural')
            )
    major = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.CheckboxWidget(category='structural')
            )
    degree = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.CheckboxWidget(category='structural')
            )
    abroad = colander.SchemaNode(
            colander.Boolean(),
            widget=deform.widget.CheckboxWidget(category='structural')
            )
    summary = colander.SchemaNode(
            colander.String(),
            widget = deform.widget.TextInputWidget(category='structural')
            )

@view_config(route_name='resume_edit2', renderer='resume_edit2.jinja2')
def resume_edit(context, request):
    pass

def includeme(config):
    settings = config.get_settings()
    config.add_route('add_resume','/add_resume')
    config.add_route('resume_edit2','/resume_edit2')
    config.scan(__name__)
