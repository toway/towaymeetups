#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

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

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user
from mba.resources import MbaUser
from mba import _

@view_config(route_name='activity', renderer='activity.jinja2')
def view_register_finish(context, request):

    resp_dict = {
        'status': 1,# 1=ON_GOING/0=FINISHED
        'status_desc': u'正在进行中...',
        'title':u'人格解析与信任建立',
        'abstract':u'简介',
        'content':u'活动介绍',
        'tips':u'xxxxx',
        'speaker':u'李玫瑾',
        'speaker_introduction':u'李玫瑾，系中国人民公安大学教授，研究生导师。中国警察协会学术委员，中国青少年犯罪研究会副会长，中国心理学会法心理学专业委员会副主任等。',
        'comments':[u'ok',u'ok2'],
        'applicants':[u'陈...',u'余争'] * 10
    }

    return resp_dict

class TagNode(colander.SequenceSchema):
    tag = colander.SchemaNode(colander.String())

class ActivitySchema(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    abstract = colander.SchemaNode(colander.String())
    content = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.RichTextWidget(theme='modern'
                , template = 'richtext.jinja2'
                , width=790
                , height=500),
        )
    tags = TagNode()

@view_config(route_name='act_add', renderer='col_test.jinja2')
def view_activity_add(context, request):
    schema = ActivitySchema().bind(request=request)
    form = deform.Form(schema,
                buttons=[deform.form.Button(u'submit', title=u'发布')])
    rendered_form = None
    if u'submit' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            rendered_form = e.render()
        else:
            print appstruct
    if rendered_form is None:
        rendered_form = form.render(request.params)
    return {'form': jinja2.Markup(rendered_form)}

@view_config(route_name="find", renderer='find.jinja2')
def view_find(context, request):
    return {'aaa':'bbb'}

def includeme(config):

    config.add_route('activity','/activity')
    config.add_route('find','/find')
    config.add_route('act_add','/act-add')
    config.scan(__name__)

