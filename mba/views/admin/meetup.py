#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, TextInputWidget, HiddenWidget, CheckboxWidget, DateInputWidget, DateTimeInputWidget
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
from kotti.resources import Node
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from kotti.views.edit.content import ContentSchema
from kotti.views.form import ObjectType
from kotti.views.form import deferred_tag_it_widget
from kotti.views.form import CommaSeparatedListWidget, get_appstruct
from kotti.fanstatic import tagit
from kotti.views.util import search_content


from mba.resources import get_act_root
from mba.resources import MbaUser
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba import _
from mba.resources import *
from mba.fanstatic import city_css

from mba.views.widget import URLInputWidget,ImageUploadWidget,ImageUploadWidget2, GeoWidget, DateTimeRangeInputWidget, DateTimeRange, CityWidget
from mba.views.view import MbaTemplateAPI


from js.jquery import jquery



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
    widget = deform.widget.SelectWidget(values=[ (str(i.id), i.title) 
                                                   for i in DBSession.query(MeetupType).all() ],
                                          css_class='form-control')
    return widget    
    
@colander.deferred
def deferred_duplicated_meetupname_validator(node, kw):    
    
    def raise_duplicated_name(node, value):
        raise colander.Invalid(
            node, _(u"已经存在的URL名!"))
    reqst = kw['request']
    

    
    if reqst.POST and 'save' in reqst.POST:
        urlname = reqst.params.get('name')
        if DBSession.query(Node).filter_by(name=urlname).count() != 0:        
            return raise_duplicated_name
        
class GeoSchema(colander.MappingSchema):
    latitude = colander.SchemaNode(colander.String(),
                                   widget=HiddenWidget())
    longitude = colander.SchemaNode(colander.String(),
                                    widget=HiddenWidget())
    zoomlevel = colander.SchemaNode(colander.Integer(),
                                    widget=HiddenWidget())

class ActSchema(colander.MappingSchema):


    title = colander.SchemaNode(
        colander.String(),
        title=_(u'标题'),
        )

    # name = colander.SchemaNode(
    #     colander.String(),
    #     title=_(u"活动URL"),
    #     description=_(u"以a-b-c形式"),
    #     widget=deferred_urlinput_widget,
    #     validator=deferred_duplicated_meetupname_validator
    # )


    # poster_id = colander.SchemaNode(
    #     colander.Integer(),
    #     title=_(u'海报'),
    #     description=_(u'上传海报'),
    #     widget=ImageUploadWidget(title=_(u"上传海报"))
    # )

    poster_img = colander.SchemaNode(
        colander.String(),
        title=_(u'海报(190px宽 x 240px高 或相应比例)'),
        description=_(u'上传海报'),
        widget=ImageUploadWidget2(title=_(u"上传海报"))

    )

    headline = colander.SchemaNode(
        colander.Integer(),
        title=_(u'是否在头条推荐：'),
        widget=CheckboxWidget(true_val="1",false_val="0"),
        default=Act.PUTONBANNER_NO
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
            , widget=CityWidget()
            )
    location = colander.SchemaNode(
        colander.String(),
        title=_(u'详细位置'),
        # widget=TextAreaWidget(cols=40, rows=5),
        missing=u"",
        )
    geo = GeoSchema(
        widget= GeoWidget(),
        # missing=u"",
    )

    def preparer(self, appstruct):
        # print 'preparer:  ',appstruct
        # popped = appstruct.pop('geo')
        #
        # appstruct.update({'latitude': popped.get('latitude',0),
        #                   'longitude':popped.get('longitude',0),
        #                   'zoomlevel':popped.get('zoomlevel',0)})
        #


        appstruct.update( appstruct.pop('geo'))
        # appstruct.update( appstruct.pop('meetup_time_range'))
        # appstruct.update( appstruct.pop('enroll_time_range'))




        popped = appstruct.pop('meetup_time_range')


        appstruct.update({'meetup_start_time': popped[0],
                          'meetup_finish_time':popped[1]
                        })

        popped = appstruct.pop('enroll_time_range')

        appstruct.update({'enroll_start_time': popped[0],
                          'enroll_finish_time':popped[1],
                        })

        city_name = appstruct.pop('city_name')
        city =  DBSession.query(City).filter_by(name=city_name).first()
        if city is not None:
            appstruct['city_id'] = city.id
        else:
            appstruct['city_name'] = city_name


        return appstruct



    meetup_time_range = colander.SchemaNode(
        DateTimeRange(default_tzinfo=None),
        widget=DateTimeRangeInputWidget(control_names=('meetup_start_time', 'meetup_finish_time')),
        title=u"活动起止时间"
    )
    enroll_time_range = colander.SchemaNode(
        DateTimeRange(default_tzinfo=None),
        widget=DateTimeRangeInputWidget(control_names=('enroll_start_time', 'enroll_finish_time')),
        title=u"报名起止时间"
    )

    # meetup_start_time = colander.SchemaNode(
    #         colander.DateTime(default_tzinfo=None),
    #         widget=DateTimeInputWidget(options = datetimeoptions),
    #         title=u'活动开始时间')
    # meetup_finish_time = colander.SchemaNode(
    #         colander.DateTime(default_tzinfo=None), title=u'活动结束时间')
    #
    # enroll_start_time = colander.SchemaNode(
    #         colander.DateTime(default_tzinfo=None), title=u'报名开始时间')
    # enroll_finish_time = colander.SchemaNode(
    #         colander.DateTime(default_tzinfo=None), title=u'报名结束时间')

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

    # use_csrf_token = False
    
    item_type = _(u"活动")

    # buttons = (
    #     deform.Button('save',_(u'发布')),
    #     deform.Button('preview',_(u'预览'))
    # )

    form_options = ({'css_class':'form-horizontal'})

    
    
    def __call__(self):
        ret = AddFormView.__call__(self)
        if isinstance(ret, dict):            
            ret = wrap_user2(self.request, ret)
            ret.update({'api': MbaTemplateAPI(self.context, self.request)})            
        return ret


            
    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        # name = self.find_name(appstruct)
        #parent_id=get_act_root().id
        parent = get_act_root()
        appstruct['__acl__'] = SITE_ACL
        new_item = self.add(default_view='test_view', **appstruct)
        parent['tempname'] = new_item
        new_item.name = new_item.position+1
        self.request.session.flash(self.success_message, 'success')
        # print 'success url:', self.request.resource_url(new_item)
        location = self.success_url or self.request.resource_url(new_item)
        if location.endswith('/'):
            location = location[:-1]
        return HTTPFound(location=location)
        
class ActEditForm(EditFormView):    

    buttons = (
        deform.Button('update', _(u'更新')),
        deform.Button('cancel', _(u'取消')))
        
    schema_factory = ActSchema


    def __init__(self, context, request, **kwargs):
        
        id = request.matchdict['id']
        meetup = DBSession.query(Act).filter_by(id=id).one()
        context = meetup
        
        EditFormView.__init__(self, context, request, **kwargs)


    def __call__(self):
        ret = EditFormView.__call__(self)
        if isinstance(ret, dict):
            ret = wrap_user2(self.request, ret)
            ret.update({'api': MbaTemplateAPI(self.context, self.request)})
        return ret

    def update_success(self, appstruct):

        return self.save_success(appstruct)

    def appstruct(self):
        # print self.context
        # print self.schema
        # print self.context.latitude
        # print self.context.longitude


        appstruct = get_appstruct(self.context, self.schema)
        lat = getattr(self.context,'latitude', 0)
        lng = getattr(self.context, 'longitude', 0)
        zoomlevel = getattr(self.context, 'zoomlevel', 0)
        appstruct.update({'geo': {'latitude':lat,
                          'longitude':lng,
                          'zoomlevel':zoomlevel}})

        mst = getattr(self.context, 'meetup_start_time', None)
        mft = getattr(self.context, 'meetup_finish_time', None)
        appstruct.update({'meetup_time_range': (mst, mft)})

        est = getattr(self.context, 'enroll_start_time', None)
        eft = getattr(self.context, 'enroll_finish_time', None)

        appstruct.update({'enroll_time_range': (est, eft)})


        return appstruct
        # return ( {'title':'sb'})
        
@view_config(route_name="find", renderer='find.jinja2')
def view_find(context, request):
    return {'aaa':'bbb'}





def view_meetup_entry(page_index=1, num_per_page=10):
    jquery.need()
    count = DBSession.query(Act).filter(Act.status!=Act.STATUS_DELETED).count()

    start = (page_index-1) * num_per_page
    result = DBSession.query(Act).filter(Act.status!=Act.STATUS_DELETED).slice(start,num_per_page)
    part = [ { 'id': it.id,
              'name': it.name,
              'title': it.title,
              'status': it.status,
              'headline': it.headline
             }
                for it in result ]

    for i in range(len(part)):
        part[i]['index'] = i+1

    total_page = count / num_per_page + 1

    return {'meetups': part,
            'total_count': count ,
            'total_page':total_page,
            'num_per_page':num_per_page,
            'page_index': 1}

# @view_config(route_name='admin', renderer='admin/meetups.jinja2', permission='manage')
# @wrap_user
# def view_admin_home(request):
#     return view_meetup_entry()

@view_config(route_name='admin_meetups', renderer='admin/meetups.jinja2',permission='view')
@view_config(route_name='admin', renderer='admin/meetups.jinja2', permission='manage')
@wrap_user
def view_meetups(request):

    if 'delete' in request.POST:
        todel = request.POST.getall('meetupcheck')

        for mid in todel:

            # print 'mid:%s, len mid:%d'% ( mid, len(mid) )
            meetup = DBSession.query(Act).filter_by(id=int(mid)).first()
            if meetup is not None :
                # print meetup
                if len(meetup.parts) != 0:
                    request.session.flash(u"活动'%s..'由于已经有人报名不能删除!" % meetup.title[:10], 'danger')

                else:
                    meetup.status = Act.STATUS_DELETED
                    request.session.flash(u"活动'%s..'已成功删除!" % meetup.title[:10], 'success')



            DBSession.flush()
        # DBSession.commit()




    return view_meetup_entry()


def includeme(config):


    config.add_route('admin','/admin')
    config.add_route('admin_meetups','/admin/meetups')
    config.add_route('admin_reviews','/admin/reviews')

    config.add_route('admin_meetup_add',  '/admin/meetup/add')
    config.add_view(ActAddForm, route_name='admin_meetup_add', renderer="admin/meetup_add.jinja2", permission='add')

    config.add_route('admin_meetup_edit',  '/admin/meetup/edit/{id}')
    config.add_view(ActEditForm, route_name='admin_meetup_edit', renderer="admin/meetup_add.jinja2", permission='edit')



    config.add_view(
        ActAddForm,
        name=Act.type_info.add_view,
        #permission='add',
        renderer='col_test.jinja2',
        )

    config.add_route('activity','/activity')
    config.add_route('find','/find')
    #config.add_route('act_add','/act-add')
    config.scan(__name__)

