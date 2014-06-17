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
from deform.widget import RichTextWidget

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user
from kotti.resources import Document
from kotti.views.form import AddFormView
from kotti.views.edit.content import ContentSchema

from mba.resources import MbaUser
from mba import _
from kotti.resources import get_root
from mba.resources import *

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
    title = colander.SchemaNode(colander.String(), title=u'标题')
    description = colander.SchemaNode(colander.String(), title=u'描述')
    body = colander.SchemaNode(
            colander.String(),
            title = u'内容',
            widget=RichTextWidget(theme='modern'
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
    appstruct = request.params
    if u'submit' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            rendered_form = e.render()
        else:
            try:
                act = Act(name=appstruct['title']
                        , parent_id = get_root().id
                        , status = ActStatus.DRAFT
                        , title=appstruct['title']
                        , description=appstruct['description']
                        , body=appstruct['body']
                        , tags=appstruct['tags'])
                DBSession.add(act)
            except:
                return {'form': "Exists"}
            else:
                return {'form': "Succeed"}
    if rendered_form is None:
        rendered_form = form.render(appstruct)
        #rendered_form = form.render({'title':'a','description':'b','body':'c','tags':['a','b','c']})
    return {'form': jinja2.Markup(rendered_form)}

class ActSchema(ContentSchema):
    body = colander.SchemaNode(
        colander.String(),
        title=_(u'Body'),
        widget=deform.widget.RichTextWidget(theme='modern'
            , template = 'richtext.jinja2'
            , width=790
            , height=500),
        )

class ActAddForm(AddFormView):
    schema_factory = ActSchema
    add = Act
    item_type = _(u"活动")

    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = self.find_name(appstruct)
        print name
        new_item = self.context[name] = self.add(default_view='test_view', **appstruct)
        self.request.session.flash(self.success_message, 'success')
        location = self.success_url or self.request.resource_url(new_item)
        return HTTPFound(location=location)

@view_config(route_name="find", renderer='find.jinja2')
def view_find(context, request):
    return {'aaa':'bbb'}

def includeme(config):
    config.add_view(
        ActAddForm,
        name=Act.type_info.add_view,
        #permission='add',
        renderer='col_test.jinja2',
        )

    config.add_route('activity','/activity')
    config.add_route('find','/find')
    config.add_route('act_add','/act-add')
    config.scan(__name__)

