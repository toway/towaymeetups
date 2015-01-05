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
from js.jqueryui import jqueryui

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user



from mba.resources import MbaUser
from mba import _
from mba.utils.decorators import wrap_user
from mba.resources import Act, Review, Participate ,Banner

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

def query_meetups(request):
    jquery.need()
    jqueryui.need()

    user = get_user(request)



    result = DBSession.query(Act).filter(Act.status==Act.STATUS_PUBLIC).limit(20)
    all = [ {'name': it.name,
             'title': it.title,
             'meetup_type' : it.meetup_type_title,
             'city': it.city_name,
             'time': it.modification_date}
                for it in result ]
    bj  = [ i for i in all if i['city'] == u"北京"]
    sh  = [ i for i in all if i['city'] == u"上海"]
    gz  = [ i for i in all if i['city'] == u"广州"]
    sz  = [ i for i in all if i['city'] == u"深圳"]
    others  = [ i for i in all
                    if i['city'] not in [u"深圳", u"广州", u"上海" , u"北京" ] ]

    result2 = DBSession.query(Review).limit(20)
    all2 = [ {'name': it.name,
             'title': it.title,
             'meetup_type' : u"志友会Dummy",
             'city': u"深圳",
               'time': it.modification_date}
                for it in result2 ]
    bj2  = [ i for i in all if i['city'] == u"北京"]
    sh2  = [ i for i in all if i['city'] == u"上海"]
    gz2  = [ i for i in all if i['city'] == u"广州"]
    sz2  = [ i for i in all if i['city'] == u"深圳"]
    others2  = [ i for i in all
                    if i['city'] not in [u"深圳", u"广州", u"上海" , u"北京" ] ]

    headline = DBSession.query(Act).filter_by(headline=1)

    my_participate = None
    if user:
        my_participate = DBSession.query(Participate).filter_by(user_id=user.id).limit(5)


    meetup_banners = DBSession.query(Banner).filter_by(status=Banner.VALID, type=Banner.TYPE_MEETUP).limit(5)

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
             'headlines': headline,
             'meetup_banners': meetup_banners,
             'my_meetups': my_participate

            }


@view_config(route_name='meetups', renderer='meetups.jinja2')
@wrap_user
def view_meetups(request):
    return query_meetups(request)




# TODO: pagnation is needed

@view_config(route_name='my_meetups', renderer='i_meetups.jinja2')
@wrap_user
def view_my_meetups(context, request):
    user = get_user(request)
    my_participate = None
    if user:
        my_participate = DBSession.query(Participate).filter_by(user_id=user.id).limit(5)

    return {'my_meetups': my_participate}

def includeme(config):
    config.add_route('meetups','/meetups')
    config.add_route('my_meetups','/i/meetups')

    config.scan(__name__)
