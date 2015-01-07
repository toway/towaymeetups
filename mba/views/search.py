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



@view_config(route_name='search_information', renderer='search_xinxi.jinja2')
def search_information(request, page_index=1, num_per_page=10):
    jquery.need()
    start = (page_index-1) * num_per_page

    vdict = ['', 'infomation', 'act', 'position']
    vmodel = [Infomation, Act, Position]
    q = request.GET.get('q', '')
    v = request.GET.get('v', '1,2,3')

    if 'q' in request.POST:
        q = request.POST['q']

    qs = ['%'+qq+'%' for qq in q.split()]
    vs = [vdict[int(vv)] for vv in v.split(',')]

    f = DBSession.query(Document).filter(or_(*[Document.type == vv for vv in vs]))
    if q:
        f = f.filter(
            or_(*[Document.title.like(term) for term in qs]))

    print 'f', f
    count = f.count()
    results = f.slice(start, num_per_page).all()

    '''
    count1 = DBSession.query(Document).filter(Document.type == 'infomation') \
                .filter(or_(*[Document.title.like(term) for term in qs])).count()
    count2 = DBSession.query(Document).filter(Document.type == 'act')   \
                .filter(or_(*[Document.title.like(term) for term in qs])).count()
    count3 = DBSession.query(Document).filter(Document.type == 'position')  \
                .filter(or_(*[Document.title.like(term) for term in qs])).count()
    '''
    counts = []
    for model in vmodel:
        model_f = DBSession.query(model)
        if q:
            model_f = model_f.filter(or_(*[Document.title.like(term) for term in qs]))
        counts.append(model_f.count())

    return wrap_user2(request, {
              'infos': results
            , 'count': count
            , 'count1': counts[0]
            , 'count2': counts[1]
            , 'count3': counts[2]
            , 'total_count': count
            , 'total_page': count/ num_per_page + 1
            , 'page_index': page_index
            })

@view_config(route_name='search_huoban', renderer='search_huoban.jinja2')
def search_huoban(request, page_index=1, num_per_page=10):
    return wrap_user2(request, {})

def includeme(config):
    config.add_route('search_information', '/search-info')
    config.add_route('search_huoban', '/search-huoban')
    config.scan(__name__)
