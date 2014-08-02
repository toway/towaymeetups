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
from kotti import DBSession

from mba import _
from mba.utils import wrap_user
from mba.resources import Student, Position

def integers(*segment_names):
    def predicate(context, request):
        match = request.matchdict
        for segment_name in segment_names:
            try:
                match[segment_name] = int(match[segment_name])
            except (TypeError, ValueError):
                return False
        return True
    return predicate

person_id_predic = integers("id")

@view_config(route_name='person', renderer='person2.jinja2', custom_predicates=(person_id_predic,))
def view_job(request):
    userid = int(request.matchdict['id'])
    user = DBSession.query(Student).get(userid)
    new_positions = DBSession.query(Position).all()[0:8]
    return wrap_user(request, {
                "person_info": user,
                "resumes": user.resumes,
                "new_positions": new_positions,
           })

def includeme(config):
    config.add_route('person','/person/{id}')
    config.scan(__name__)
