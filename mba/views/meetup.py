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
from kotti.interfaces import IContent

from mba.resources import MbaUser, TZ_HK
from mba import _
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2

__author__ = 'sunset'
__date__ = '20140614'



@view_config(name='test_view', context=IContent, renderer='meetup.jinja2')
def view_meetup(context, request):  
    jquery.need()    
    contextbody = jinja2.Markup(context.body)
    # print 'timenow ', datetime.now(TZ_HK)
    print 'enroll time ', context.enroll_start_time
    # context.enroll_start_time = context.enroll_start_time.replace(tzinfo = TZ_HK )
    # print 'enroll time2 ', context.enroll_start_time
    # context.enroll_finish_time =  context.enroll_finish_time.replace(tzinfo = TZ_HK )
    # context.meetup_start_time = context.meetup_start_time.replace(tzinfo = TZ_HK )
    # context.meetup_finish_time= context.meetup_finish_time.replace(tzinfo = TZ_HK )
    
    enrolled = False

    print 'context'
    print context
    print 'context._parts'
    print context._parts
    print 'context.parts'
    print context.parts    
    
    if request.POST and "enroll" in request.POST:
        # enroll this 
        user = get_user(request)
        if user is None:
            return HTTPFound("/login")
        

        context._parts.append(user)
        enrolled = True
        
    return  wrap_user2(request, 
                {'context':context, 
                'contextbody': contextbody,
                # 'time_now': datetime.now(TZ_HK)
                'time_now': datetime.now(),
                'enrolled': enrolled
                })


def includeme(config):
    config.add_route('meetup','/meetup')
    config.scan(__name__)
