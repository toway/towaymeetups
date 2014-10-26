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


from kotti import DBSession

from mba.resources import get_act_root
from mba.resources import MbaUser, Act, Review
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.fanstatic import city_css
from mba.views.widget import URLInputWidget
from mba.views.view import MbaTemplateAPI
from mba.views.review import ReviewAddForm, ReviewEditForm
from mba import _


from js.jquery import  jquery

def view_review_entry(page_index=1, num_per_page=10):
    jquery.need()
    queried = DBSession.query(Review)
    count = queried.count()
    start = (page_index-1) * num_per_page
    result = DBSession.query(Review).slice(start,num_per_page)
    part = [ { 'id': it.id,
              'name': it.name,
              'title': it.title
             }
                for it in result ]

    for i in range(len(part)):
        part[i]['index'] = i+1

    total_page = count / num_per_page + 1

    return {'reviews': part,
            'total_count': count ,
            'total_page':total_page,
            'num_per_page':num_per_page,
            'page_index': 1}


@view_config(route_name='admin_reviews', renderer='admin/reviews.jinja2',permission='view')
@wrap_user
def view_reviews(request):
    return view_review_entry()


def includeme(config):

    config.add_route('admin_review_add',  '/admin/review/add')
    config.add_view(ReviewAddForm, route_name='admin_review_add', renderer="admin/meetup_add.jinja2", permission='view')


    config.add_route('admin_review_edit',  '/admin/review/edit/{id}')
    config.add_view(ReviewEditForm, route_name='admin_review_edit', renderer="admin/meetup_add.jinja2", permission='view')
