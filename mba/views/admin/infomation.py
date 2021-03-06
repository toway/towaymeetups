#!/usr/bin/python
# coding: utf-8

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
from pyramid.request import Response

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user


from mba import _
from mba.utils.decorators import wrap_user
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import Infomation

__author__ = 'sunset'
__date__ = '20140904'
__description__ = u'管理员的推荐信息'


from js.jquery import jquery


INFO_NUM_PER_PAGE = 20

def view_info_entry(page_index=1, num_per_page=10):
    jquery.need()
    queried = DBSession.query(Infomation).filter_by(status=Infomation.STATUS_PUBLIC)
    count = queried.count()
    start = (page_index-1) * num_per_page
    result = DBSession.query(Infomation).filter_by(status=Infomation.STATUS_PUBLIC).slice(start,num_per_page)
    part = [ { 'id': it.id,
              'name': it.name,
              'title': it.title
             }
                for it in result ]

    for i in range(len(part)):
        part[i]['index'] = i+1

    total_page = count / num_per_page + 1

    return {'infomations': part,
            'total_count': count ,
            'total_page':total_page,
            'num_per_page':num_per_page,
            'page_index': 1}


@view_config(route_name='admin_infomations_id', renderer='admin/infomations.jinja2')
@view_config(route_name='admin_infomations', renderer='admin/infomations.jinja2',permission='view')
@wrap_user
def view_reviews(request):
    if 'delete' in request.POST:
        todel = request.POST.getall('infocheck')

        for mid in todel:

            # print 'mid:%s, len mid:%d'% ( mid, len(mid) )
            info = DBSession.query(Infomation).filter_by(id=int(mid)).first()
            if info is not None :

                info.status = Infomation.STATUS_DELETED
                request.session.flash(u"信息'%s...'已成功删除!" % info.title[:10], 'success')



            DBSession.flush()


    pageid = int(request.matchdict.get('id',1) )
    retobj =  view_info_entry(pageid, INFO_NUM_PER_PAGE)
    retobj.update({'urlprifix': '/admin/infomations'})

    return retobj


def includeme(config):



    config.add_route('admin_infomations','/admin/infomations')
    config.add_route('admin_infomations_id','/admin/infomations/{id}')

    config.add_route('admin_info_add',  '/admin/infomation/add')
    config.add_view(InfoAddForm, route_name='admin_info_add', renderer="admin/meetup_add.jinja2", permission='view')

    config.add_route('admin_info_edit',  '/admin/infomation/edit/{id}')
    config.add_view(InfoEditForm, route_name='admin_info_edit', renderer="admin/meetup_add.jinja2", permission='view')


    config.scan(__name__)
