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

from js.jquery import jquery

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user



from mba.resources import MbaUser
from mba import _
from mba.utils.decorators import wrap_user
from mba.resources import Act, Review, Participate, Infomation
from mba.views.admin.infomation import view_info_entry, INFO_NUM_PER_PAGE

__author__ = 'sunset'
__date__ = '201401224'

# INFO_NUM_PER_PAGE = 20


# def view_info(page_index=1):
#     jquery.need()
#
#     start = (page_index-1) * INFO_NUM_PER_PAGE
#
#     count = DBSession.query(Infomation).count()
#     infomations = DBSession.query(Infomation).slice(start, INFO_NUM_PER_PAGE).all()
#
#
#     return {
#         'infomations': infomations,
#         'total_count': count,
#         'total_page': count/ INFO_NUM_PER_PAGE + 1,
#         'page_index': page_index
#     }


@view_config(route_name='infomations_id', renderer='infomations.jinja2')
@view_config(route_name='infomations', renderer='infomations.jinja2')
@wrap_user
def query_infomations(request):
    jquery.need()

    # user = get_user(request)

    pageid = int(request.matchdict.get('id',1) )
    retobj =  view_info_entry(pageid, INFO_NUM_PER_PAGE)
    retobj.update({'urlprifix': '/infomations'})

    return retobj





def includeme(config):
    config.add_route('infomations','/infomations')
    config.add_route('infomations_id','/infomations/{id}')

    config.scan(__name__)
