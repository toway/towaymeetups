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
from mba.views.activity import ActAddForm, ActEditForm
from mba.views.review import ReviewEditForm, ReviewAddForm
from mba.resources import MbaUser, Act, Review
__author__ = 'sunset'
__date__ = '20140614'


from js.jquery import jquery


def view_meetup_entry(page_index=1, num_per_page=10):
    jquery.need()
    queried = DBSession.query(Act)
    count = queried.count()
    start = (page_index-1) * num_per_page
    result = DBSession.query(Act).slice(start,num_per_page)
    part = [ { 'id': it.id,
              'name': it.name, 
              'title': it.title
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

@view_config(route_name='admin', renderer='admin/meetups.jinja2')
@wrap_user
def view_admin_home(request):
    return view_meetup_entry()

@view_config(route_name='admin_meetups', renderer='admin/meetups.jinja2')
@wrap_user
def view_meetups(request):     
    return view_meetup_entry()
    
    
    
    
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
    

@view_config(route_name='admin_reviews', renderer='admin/reviews.jinja2')
@wrap_user
def view_reviews(request):     
    return view_review_entry()    
            

    

# @view_config(route_name='admin_meetup_edit', renderer="admin/meetup_add.jinja2")
# def edit_meetup(context, request):
    # meetup_id = request.matchdict['id']
    # return ActEditForm()
    
def view_response_test(request):
    return Response("SB")

def includeme(config):
    config.add_route('admin','/admin')
    config.add_route('admin_meetups','/admin/meetups')
    config.add_route('admin_reviews','/admin/reviews')
    
    config.add_route('admin_meetup_add',  '/admin/meetup/add')
    config.add_view(ActAddForm, route_name='admin_meetup_add', renderer="admin/meetup_add.jinja2")
    
    config.add_route('admin_meetup_edit',  '/admin/meetup/edit/{id}')
    config.add_view(ActEditForm, route_name='admin_meetup_edit', renderer="admin/meetup_add.jinja2")    
    
    config.add_route('admin_review_add',  '/admin/review/add')
    config.add_view(ReviewAddForm, route_name='admin_review_add', renderer="admin/meetup_add.jinja2")      
    
    # config.add_route('admin_review_add',  '/admin/review/add?meetup-id={id}')
    # config.add_view(ReviewAddForm, route_name='admin_review_add', renderer="admin/meetup_add.jinja2")        

    # config.add_route('admin_review_add3',  '/admin/review/add/{id}')
    # config.add_view(ReviewAddForm, route_name='admin_review_add3', renderer="admin/meetup_add.jinja2")            

    config.add_route('admin_review_edit',  '/admin/review/edit/{id}')
    config.add_view(ReviewEditForm, route_name='admin_review_edit', renderer="admin/meetup_add.jinja2")    



    config.scan(__name__)
