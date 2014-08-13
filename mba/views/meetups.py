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
from mba.resources import Act, Review

__author__ = 'sunset'
__date__ = '20140527'

'''
@view_config(route_name='meetups', renderer='meetups-pjax.jinja2', header='X-PJAX')
def view_meetups_pjax(request):
    if not get_user(request):
        return HTTPFound("/login")

    if 'X-PJAX' in request.headers:
        print('pjax in')

    return {'a':'b'}
    #return Response("Pjax Meet Ups !")

'''

@view_config(route_name='meetups', renderer='meetups.jinja2')
@wrap_user
def view_meetups(request):
    jquery.need()
    
    result = DBSession.query(Act).limit(20)
    all = [ {'name': it.name, 
             'title': it.title,
             'meetup_type' : it.meetup_type_title,
             'city': it.city_name} 
                for it in result ]    
    bj  = [ i for i in all if i['city'] == u"北京"]           
    sh  = [ i for i in all if i['city'] == u"上海"]           
    gz  = [ i for i in all if i['city'] == u"广州"]           
    sz  = [ i for i in all if i['city'] == u"深圳"]
    others  = [ i for i in all 
                    if i['city'] != u"深圳" and i['city'] != u"广州"
                       and i['city'] != u"上海" and i['city'] != u"北京" ]

    result2 = DBSession.query(Review).limit(20)
    all2 = [ {'name': it.name, 
             'title': it.title,
             'meetup_type' : u"志友会Dummy",
             'city': u"深圳"} 
                for it in result2 ]    
    bj2  = [ i for i in all if i['city'] == u"北京"]           
    sh2  = [ i for i in all if i['city'] == u"上海"]           
    gz2  = [ i for i in all if i['city'] == u"广州"]           
    sz2  = [ i for i in all if i['city'] == u"深圳"]
    others2  = [ i for i in all 
                    if i['city'] != u"深圳" and i['city'] != u"广州"
                       and i['city'] != u"上海" and i['city'] != u"北京" ]


    headline = DBSession.query(Act).filter_by(headline=1)
    
    return { 'meetups': 
                {'all': all,
                 'first_five': all[:5],
                'bj': bj,
                'sh': sh,
                'gz': gz,
                'sz': sz,
                'others':others},
             'reviews':
                {'all': all2,
                 'first_five': all2[:5],
                'bj': bj2,
                'sh': sh2,
                'gz': gz2,
                'sz': sz2,
                'others':others2},
             'headlines': headline

            } 


def includeme(config):
    config.add_route('meetups','/meetups')
    config.scan(__name__)
