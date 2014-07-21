#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, TextInputWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email
from deform.widget import RichTextWidget
from deform.widget import TextAreaWidget

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user
from kotti.resources import Document
from kotti.views.form import AddFormView
from kotti.views.edit.content import ContentSchema
from kotti.views.form import ObjectType
from kotti.views.form import deferred_tag_it_widget
from kotti.views.form import CommaSeparatedListWidget
from kotti.fanstatic import tagit
from kotti.views.util import search_content

from mba.resources import get_act_root
from mba.resources import MbaUser
from mba.utils import wrap_user
from mba import _
from mba.resources import *
from mba.fanstatic import city_css

from mba.views.widget import URLInputWidget

@view_config(route_name='activity', renderer='activity.jinja2')
def view_activity(context, request):
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

    return wrap_user(request, resp_dict)

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

#@view_config(route_name='act_add', renderer='col_test.jinja2')
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
                        , parent_id = get_act_root().id
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

@colander.deferred
def deferred_teachertag_it_widget(node, kw):
    tagit.need()
    all_tags = TeacherTag.query.all()
    available_tags = [tag.title.encode('utf-8') for tag in all_tags]
    widget = CommaSeparatedListWidget(template='tag_it',
                                      available_tags=available_tags)
    return widget

@colander.deferred
def deferred_city_widget(node, kw):
    city_css.need()
    widget = TextInputWidget(template='text_input_city')
    return widget
    
@colander.deferred
def deferred_urlinput_widget(node, kw):
    
    request = kw['request']
    widget = URLInputWidget(url_prefix=request.application_url + "/meetup/")
    return widget    

@colander.deferred
def deferred_meetuptypes_widget(node, kw):
    widget = deform.widget.SelectWidget(values=[ (i.id, i.title) 
                                                   for i in DBSession.query(MeetupType).all() ],
                                          css_class='form-control')
    return widget    
    
    
class ActSchema(colander.MappingSchema):
    title = colander.SchemaNode(
        colander.String(),
        title=_(u'标题'),
        )
    name = colander.SchemaNode(
        colander.String(),
        title=_(u"活动URL"),
        description=_(u"以a-b-c形式"),
        widget=deferred_urlinput_widget
    )
    

    meetup_type = colander.SchemaNode(
        colander.Integer(),
        title=_(u'活动类型'),
        widget=deferred_meetuptypes_widget
    )    

    description = colander.SchemaNode(
        colander.String(),
        title=_('Description'),
        widget=TextAreaWidget(cols=40, rows=5),
        missing=u"",
        )

    teachers = colander.SchemaNode(
        ObjectType(),
        title=_(u'老师'),
        widget=deferred_teachertag_it_widget,
        missing=[],
        )
    city_name = colander.SchemaNode(colander.String()
            , title=_(u"城市")
            , widget=deferred_city_widget
            )
    location = colander.SchemaNode(
        colander.String(),
        title=_(u'详细位置'),
        widget=TextAreaWidget(cols=40, rows=5),
        missing=u"",
        )
    meetup_start_time = colander.SchemaNode(
            colander.DateTime(), title=u'活动开始时间')
    meetup_finish_time = colander.SchemaNode(
            colander.DateTime(), title=u'活动结束时间')

    enroll_start_time = colander.SchemaNode(
            colander.DateTime(), title=u'报名开始时间')
    enroll_finish_time = colander.SchemaNode(
            colander.DateTime(), title=u'报名结束时间')

    limit_num = colander.SchemaNode(
            colander.Integer(), title=u'人数限制', default=500)
    pay_count = colander.SchemaNode(
            colander.Integer(), title=u'支付', default=0)

    body = colander.SchemaNode(
        colander.String(),
        title=_(u'Body'),
        widget=RichTextWidget(theme='modern', width=790, height=500),

        )
    tags = colander.SchemaNode(
        ObjectType(),
        title=_('Tags'),
        widget=deferred_tag_it_widget,
        missing=[],
        )

class ActAddForm(AddFormView):
    schema_factory = ActSchema
    add = Act
    
    
    item_type = _(u"活动")

    form_options = ({'css_class':'form-horizontal'})
    
    
    

    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = self.find_name(appstruct)
        #parent_id=get_act_root().id
        parent = get_act_root()
        new_item = parent[name] = self.add(default_view='test_view', **appstruct)
        self.request.session.flash(self.success_message, 'success')
        location = self.success_url or self.request.resource_url(new_item)
        return HTTPFound(location=location)

class PositionSchema(ContentSchema):
    job_name = colander.SchemaNode(colander.String(), title=_(u"职位名字"))
    company_name = colander.SchemaNode(colander.String(), title=_(u"公司名字"))
    degree = colander.SchemaNode(colander.String(), title=_(u"学位要求"))
    experience = colander.SchemaNode(colander.String(), title=_(u"经验要求"))
    salary = colander.SchemaNode(colander.Integer(), title=_(u"待遇"))
    body = colander.SchemaNode(
            colander.String(),
            title = u'内容',
            widget=RichTextWidget(theme='modern'
                , template = 'richtext.jinja2'
                , width=790
                , height=500),
        )

class PositionAddForm(AddFormView):
    schema_factory = PositionSchema
    add = Position
    item_type = _(u"职位")

    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = self.find_name(appstruct)
        #TODO for default_view
        new_item = self.context[name] = self.add(**appstruct)
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

    config.add_view(
        PositionAddForm,
        name=Position.type_info.add_view,
        renderer='col_test.jinja2',
        )

    config.add_route('activity','/activity')
    config.add_route('find','/find')
    #config.add_route('act_add','/act-add')
    config.scan(__name__)

