# coding: utf-8

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, TextInputWidget, HiddenWidget, CheckboxWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email
from deform.widget import RichTextWidget
from deform.widget import TextAreaWidget

from sqlalchemy import and_
from sqlalchemy import not_
from sqlalchemy import or_
from  sqlalchemy.sql.expression import func

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

from mba.views.widget import URLInputWidget,ImageUploadWidget, GeoWidget
from mba.views.view import MbaTemplateAPI

default_date = datetime.strptime('1990-1-1','%Y-%m-%d').date()
class PositionSchema(ContentSchema):
    title = colander.SchemaNode(colander.String(), title=_(u"职位名字"))
    degree = colander.SchemaNode(colander.String(), title=_(u"学位要求"))
    experience = colander.SchemaNode(colander.String(), title=_(u"经验要求"))
    salary = colander.SchemaNode(colander.Integer(), title=_(u"待遇"))
    
    city_name = colander.SchemaNode(
            colander.String(),
            title = u'城市',
        )

    hunting_type = colander.SchemaNode(
        colander.Integer(),
        title=_(u'职位类型'),
        widget = deform.widget.SelectWidget(values=[ (0, _(u"公司")), (1, _(u"猎头")) ])
    )    

    public_date = colander.SchemaNode(
            colander.Date(),
            #'%Y-%m-%d %H:%M:%S'
            default=default_date,
            title=_(u"发布时间"),
            )
    end_date = colander.SchemaNode(
            colander.Date(),
            #'%Y-%m-%d %H:%M:%S'
            default=default_date,
            title=_(u"结束时间"),
            )
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
    company_id = 1

    def __init__(self, context, request, **kwargs):
        context = DBSession.query(Node).filter_by(name="position").one()
        AddFormView.__init__(self, context, request, **kwargs)
        try:
            self.company_id = request.matchdict['cid']
        except:
            pass

    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = self.find_name(appstruct)
        new_item = self.context[name] = self.add(company_id=self.company_id, **appstruct)
        self.request.session.flash(self.success_message, 'success')
        location = self.success_url or self.request.resource_url(new_item)
        return HTTPFound(location=location)

@view_config(route_name='job_view', renderer='job2.jinja2')
@wrap_user
def job_view(context, request):
    user = get_user(request)
    if not user:
        raise UserNotFount()

    pos_normals = DBSession.query(Position).filter_by(hunting_type=0).order_by(Position.salary.desc())[0:5]
    pos_huntings = DBSession.query(Position).filter_by(hunting_type=1).order_by(Position.salary.desc())[0:5]

    interest = ""
    if user.interest:
        interest = user.interest
    industry = ""
    if user.industry:
        industry = user.industry
    if interest == "" and industry == "":
        pos_like = DBSession.query(Position).all()[0:5]
    else:
        pos_like = DBSession.query(Position).join(CompanyInfo).filter(
                or_(Position.title.like(interest)
                    , CompanyInfo.industry.like(industry)) )[0:5]

    return {
            'pos_normals':pos_normals,
            'pos_huntings':pos_huntings,
            'pos_like': pos_like,
            }

@view_config(route_name='job_detail', renderer='job2_deatil.jinja2')
@wrap_user
def job_detail_view(context, request):
    pos_id = request.matchdict['id']
    pos_id = int(pos_id)
    
    user = get_user(request)
    interest = ""
    if user.interest:
        interest = user.interest
    industry = ""
    if user.industry:
        industry = user.industry
    if interest == "" and industry == "":
        pos_like = DBSession.query(Position).all()[0:5]
    else:
        pos_like = DBSession.query(Position).join(CompanyInfo).filter(
                or_(Position.title.like(interest)
                    , CompanyInfo.industry.like(industry)) )[0:5]

    pos = DBSession.query(Position).get(pos_id)

    return {
            'pos': pos,
            'pos_like': pos_like,
            }

@view_config(route_name='job_company_info', renderer='job2_company_info.jinja2')
def job_companyinfo_view(context, request):
    return {}

@view_config(route_name='job_real', renderer='job2_real.jinja2')
def job_real_view(context, request):
    return {}

@view_config(route_name='job_combine', renderer='job2_combine.jinja2')
def job_combine_view(context, request):
    return {}

@view_config(route_name='job_shenqing', renderer='job2_shenqing_more.jinja2')
def job_shenqing_view(context, request):
    return {}

#	templates/job2_combine.jinja2
#	templates/job2_company_info.jinja2
#	templates/job2_detail.jinja2
#	templates/job2_real.jinja2
#	templates/job2_shenqing_more.jinja2


def includeme(config):
    config.add_view(
        PositionAddForm,
        name=Position.type_info.add_view,
        renderer='col_test.jinja2',
        )
    config.add_route('job_view','/job')
    config.add_route('job_detail','/job-detail/{id:\d+}')
    config.add_route('job_company_info','/job-company')
    config.add_route('job_shenqing','/job-apply')
    config.add_route('job_combine','/job-combine')
    config.add_route('job_real','/job-real')
    config.scan(__name__)
