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
try:
    from sqlalchemy.exceptions import IntegrityError
except ImportError:
    from sqlalchemy.exc import IntegrityError

from sqlalchemy import and_
from sqlalchemy import not_
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from sqlalchemy import or_
from pyramid.response import Response

from js.jquery import jquery

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
            self.company_id = request.params['cid']
        except:
            pass

    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = self.find_name(appstruct)
        print self.add
        new_item = self.context[name] = self.add(company_id=self.company_id, **appstruct)
        self.request.session.flash(self.success_message, 'success')
        location = self.success_url or self.request.resource_url(new_item)
        print new_item.id
        return HTTPFound(location=location)

class CompanySchema(colander.Schema):
    name = colander.SchemaNode(colander.String(), title=_(u"公司名字"))
    type_info = colander.SchemaNode(colander.String(), title=_(u"公司性质"))
    scope = colander.SchemaNode(colander.String(), title=_(u"公司规模"))
    industry = colander.SchemaNode(colander.String(), title=_(u"公司行业"))
    location = colander.SchemaNode(colander.String(), title=_(u"公司地址"))
    description = colander.SchemaNode(
            colander.String(),
            title = u'公司描述',
            widget=RichTextWidget(theme='modern'
                , template = 'richtext.jinja2'
                , width=790
                , height=500),
        )

@view_config(route_name='add_company', renderer='col_test.jinja2')
def company_add(context, request):
    schema = CompanySchema().bind(request=request)

    form = deform.Form(schema, buttons=('Save', 'Cancel')) ;
    rendered_form = None

    if 'Save' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"添加失败" ), 'error')
            rendered_form = e.render()
        else:
            company = CompanyInfo(**appstruct)
            DBSession.add(company)
            DBSession.flush()
            url = '/job-company/%d' % company.id
            return HTTPFound(location=url)

    if rendered_form is None:
        rendered_form = form.render(request.params)

    return  {'form': jinja2.Markup(rendered_form)}

@view_config(route_name='edit_company', renderer='col_test.jinja2')
def company_edit(context, request):
    pass

@view_config(route_name='job_view', renderer='job2.jinja2')
@wrap_user
def job_view(context, request):
    jquery.need()

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

    pos_apply = DBSession.query(Position).join(PositionResume).filter(PositionResume.resume_id==user.id)

    return {
            'pos_normals':pos_normals,
            'pos_huntings':pos_huntings,
            'pos_like': pos_like,
            'pos_apply': pos_apply,
            'collects': user.positions,
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
    id = request.matchdict['id']
    id = int(id)
    try:
        company = DBSession.query(CompanyInfo).get(id)
    except:
        pass

    return {'company':company}

@view_config(route_name='job_real', renderer='job2_real.jinja2')
def job_real_view(context, request):
    return {}

@view_config(route_name='job_combine', renderer='job2_combine.jinja2')
def job_combine_view(context, request):
    return {}

@view_config(route_name='job_shenqing', renderer='job2_shenqing_more.jinja2')
def job_shenqing_view(context, request):
    return {}

@view_config(route_name='job_postit')
def job_postit_view(context, request):
    pos_id = request.matchdict['id']
    pos_id = int(pos_id)
    
    user = get_user(request)

    if not user.resume:
        user.resume = Resume()
        DBSession.flush()

    dup = False
    try:
        pr = PositionResume(position_id=pos_id, resume_id = user.resume.id)
        DBSession.add(pr)
        DBSession.flush()
    except IntegrityError:
        dup = True
    if dup:
        return Response('dup')
    else:
        return Response('ok')

@view_config(route_name='job_collect')
def job_collect_view(context, request):
    pos_id = request.matchdict['id']
    pos_id = int(pos_id)

    user = get_user(request)
    try:
        pos = DBSession.query(Position).get(pos_id)
        if pos not in user.positions:
            user.positions.append(pos)
    except:
        return Response("error")
    return Response("ok")

@view_config(route_name='job_search', renderer='job2_search_result.jinja2')
def job_search(context, request):
    city = ""
    industy = ""
    hunting = 2
    keyword = ""
    try:
        city = request.params['city']
    except:
        pass
    try:
        industy = request.params['ind']
    except:
        pass
    try:
        hunting = int(request.params['hun'])
    except:
        pass
    try:
        keyword = request.params['key']
    except:
        pass

    filters = []
    if city != "":
        filters.append(Position.city_name.like(u'%%%s%%' % city))
    if industy != "":
        filters.append(CompanyInfo.industry.like(u'%%%s%%' % industy))
    if hunting != 2:
        filters.append(Position.hunting_type == hunting)

    filter1 = None
    if len(filters) == 1:
        filter1 = filters[0]
    elif len(filters) == 2:
        filter1 = and_(filters[0], filters[1])
    elif len(filters) == 3:
        filter1 = and_(filters[0], filters[1], filters[2])

    filter_all = None
    if keyword != "":
        if filter1 is None:
            filter_all = or_(Position.title.like(u'%%%s%%' % keyword)
                    , CompanyInfo.name.like(u'%%%s%%' % keyword))
        else:
            filter_all = and_(filter1, or_(Position.title.like(u'%%%s%%' % keyword)
                    , CompanyInfo.name.like(u'%%%s%%' % keyword)))
    else:
        filter_all = filter1

    if filter_all is None:
        results = DBSession.query(Position).all()
    else:
        results = DBSession.query(Position).join(CompanyInfo).filter(filter_all).all()

    return {
            'city': city,
            'industy': industy,
            'hunting': hunting,
            'keyword': keyword,
            'results':results
            , 'result_len':len(results)}

def includeme(config):
    config.add_view(
        PositionAddForm,
        name=Position.type_info.add_view,
        renderer='col_test.jinja2',
        )
    config.add_route('add_company','/add-company')
    config.add_route('edit_company','/edit-company')
    config.add_route('job_view','/job')
    config.add_route('job_detail','/job-detail/{id:\d+}')
    config.add_route('job_postit','/job-postit/{id:\d+}')
    config.add_route('job_collect','/job-collect/{id:\d+}')
    config.add_route('job_company_info','/job-company/{id:\d+}')
    config.add_route('job_shenqing','/job-apply')
    config.add_route('job_combine','/job-combine')
    config.add_route('job_real','/job-real')
    config.add_route('job_search','/job-search')
    config.scan(__name__)
