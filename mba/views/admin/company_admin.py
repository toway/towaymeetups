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

@view_config(route_name='admin_company_add', renderer='admin/company_add.jinja2')
@wrap_user
def admin_company_add(context, request):
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

@view_config(route_name='admin_company_edit', renderer='col_test.jinja2')
def admin_company_edit(context, request):
    pass

def view_company_list(request, page_index=1, num_per_page=10):
    jquery.need()
    start = (page_index-1) * num_per_page
    count = DBSession.query(CompanyInfo).count()
    companies = DBSession.query(CompanyInfo).slice(start, num_per_page).all()

    return wrap_user2(request, {
        'companies': companies,
        'total_count': count,
        'total_page': count/ num_per_page + 1,
        'page_index': page_index
    })

@view_config(route_name='admin_company_list', renderer='admin/companies.jinja2')
@view_config(route_name='admin_company_list', renderer='json', xhr=True)
def admin_company_list(request):
    return view_company_list(request)

def includeme(config):
    config.add_route('admin_company_add','/admin/company/add')
    config.add_route('admin_company_edit','/admin/company/edit')
    config.add_route('admin_company_list','/admin/companies')
    config.scan(__name__)
