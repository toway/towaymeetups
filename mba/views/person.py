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
from pyramid.response import Response

from js.jquery import jquery
from js.jqueryui import jqueryui
from js.jquery_form import jquery_form

from kotti import get_settings
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from kotti import DBSession
from kotti.security import get_user

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

class PersonInfoWidget(object):
    renderer = staticmethod(deform.Form.default_renderer)
    def __init__(self, user):
        self.user = user
        self.template = 'person_form.jinja2'

    def render(self):
        return self.renderer(self.template, person_info=self.user)

@view_config(route_name='person', renderer='person.jinja2', custom_predicates=(person_id_predic,))
def view_person(request):
    jquery.need()
    jqueryui.need()
    jquery_form.need()

    curr_user = get_user(request)

    if "hd_id" in request.POST:
        try:
            post = request.POST
            userid = int(post['hd_id'])
            user = DBSession.query(Student).get(userid)
            if curr_user.id != user.id:
                return Response("ERROR")
            user.email = post['email']
            user.phone = post['phone']
            user.company = post['company']
            user.industry = post['industry']
            user.location = post['location']
            user.school = post['school']
            user.special_skill = post['special_skill']
            user.interest = post['interest']
            user.between = post['between']
            user.introduction = post['introduction']
            person_info_widget = PersonInfoWidget(user)
            return Response(person_info_widget.render())
        except:
            return Response("ERROR")
    
    userid = int(request.matchdict['id'])
    user = DBSession.query(Student).get(userid)
    new_positions = DBSession.query(Position).all()[0:8]
    person_info_widget = PersonInfoWidget(user)
    toknown_list = DBSession.query(Student).filter(Student.id != curr_user.id)[0:8]
    user_status = 0
    if curr_user.id == user.id:
        user_status = 1
    elif user in curr_user.all_friends:
        user_status = 2

    return wrap_user(request, {
                "person_info": user,
                "user_status": user_status,
                "curr_id": curr_user.id,
                "resumes": user.resumes,
                "new_positions": new_positions,
                "person_info_form": person_info_widget.render(),
                "toknown_list": toknown_list,
           })

@view_config(route_name='friend_set')
def friend_set(request):
    curr_user = get_user(request)
    id1 = int(request.matchdict['id1'])
    id2 = int(request.matchdict['id2'])
    id3 = int(request.matchdict['id3'])
    if (not curr_user) or (curr_user.id != id1) or id1 == id2:
        return Response("1")
    else:
        is_error = False
        u2 = DBSession.query(Student).filter(Student.id == id2).one()
        if not u2:
            return Response("1")
        if id3 > 0 and u2 not in curr_user.friends:
            try:
                curr_user.friends.append(u2)
            except:
                is_error = True
        if id3 <= 0 and u2 in curr_user.friends:
            try:
                curr_user.friends.remove(u2)
            except:
                is_error = True
        if is_error:
            return Response("1")
        else:
            return Response("0")

def includeme(config):
    config.add_route('person','/person/{id}')
    config.add_route('friend_set','/friend_set/{id1:\d+}/{id2:\d+}/{id3:\d+}')
    config.scan(__name__)
