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
from mba.utils.decorators import wrap_user as wrap_user2
from mba.utils import wrap_user
from mba.utils.sms import SMSSender
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import MbaUser, Student


__author__ = 'sunset'
__date__ = '20140909'
__description__ = u'用户管理'


from js.jquery import jquery



def view_persons(request, page_index=1, num_per_page=10):
    jquery.need()

    # print request.application_url
    # # print request.route_path()
    # print request.current_route_path()
    #
    # for i in dir(request):
    #     print request[i]

    #TODO: Do I need to judge if the user is logged in here?
    if 'method' in request.POST:

        try:
            method = request.POST['method'] # pass-iauth, cancel-iauth, fail-iauth
            personid = request.POST['person-id']

            person = DBSession.query(MbaUser).filter_by(id=personid).first()
            if not person :
                raise Exception(u"没有该用户!")

            # 0, unauthed, 1 authed, 2 authfail, ( 3 request for auth?)
            if method == 'pass-auth-info':
                person.auth_info = person.AUTH_STATUS_AUTHED
                # person.active = True
                person.status = person.ACTIVE
                sms = SMSSender(request)
                sms.send_auth_pass_sms(person.phone)
                request.session.flash(u"用户'%s'通过资料认证成功并激活" % (person.real_name or person.name) , 'success' )

            # elif method == 'cancel-iauth':
            #     person.auth_info = 0
            #     request.session.flash(u"用户'%s'取消认证成功" % (person.real_name or person.name) , 'success' )

            elif method == 'fail-auth-info':
                person.auth_info = person.AUTH_STATUS_FAIL
                request.session.flash(u"用户'%s'不通过资料认证成功" % (person.real_name or person.name) , 'success' )

            elif method == 'pass-auth-expert':
                person.auth_expert = person.AUTH_STATUS_AUTHED
                request.session.flash(u"用户'%s'通过专家认证成功" % (person.real_name or person.name) , 'success' )

            elif method == 'fail-auth-expert':
                person.auth_expert = person.AUTH_STATUS_FAIL
                request.session.flash(u"用户'%s'不通过专家认证成功" % (person.real_name or person.name) , 'success' )


        except Exception,ex:
            err_msg = "%s" % ex
            request.session.flash(_(u"错误：'%s'" % err_msg), 'danger')

        finally:
            return {}


    if 'delete-user' in request.POST:
        todel = request.POST.getall('usercheck')

        for mid in todel:

            # print 'mid:%s, len mid:%d'% ( mid, len(mid) )
            userx = DBSession.query(MbaUser).filter_by(id=int(mid)).first()
            if userx is not None :
                # DBSession.delete(userx)
                userx.status = userx.BANNED
                request.session.flash(u"用户'%s..'已成功删除!" % userx.real_name, 'success')


            DBSession.flush()


    start = (page_index-1) * num_per_page
    count = DBSession.query(MbaUser).filter(MbaUser.status!=MbaUser.BANNED).count()
    persons = DBSession.query(MbaUser).filter(MbaUser.status!=MbaUser.BANNED).slice(start, start+num_per_page).all()


    return wrap_user(request, {
        'persons': persons,
        'total_count': count,
        'total_page': (count-1)/ num_per_page + 1,
        'page_index': page_index,
        'url_prefix': '/admin/persons/page'
    })

def view_persons_by_auth(request, page_index=1, num_per_page=10, authed=Student.AUTH_STATUS_UNAUTH):
    jquery.need()

    start = (page_index-1) * num_per_page

    count = DBSession.query(Student).filter_by(auth_info=authed).count()
    persons = DBSession.query(Student).filter_by(auth_info=authed).slice(start, start+num_per_page).all()


    url_prefix = request.url
    import re
    if re.match('.*/\d{1,10}$', url_prefix):
        url_prefix = url_prefix[ : url_prefix.rfind('/') ]



    return {
        'persons': persons,
        'total_count': count,
        'total_page': count/ num_per_page + 1,
        'page_index': page_index,
        'url_prefix': url_prefix
    }

def view_persons_by_expert_auth(request, page_index=1, num_per_page=10, authed=Student.AUTH_STATUS_UNAUTH):
    jquery.need()

    start = (page_index-1) * num_per_page

    count = DBSession.query(Student).filter_by(auth_expert=authed).count()
    persons = DBSession.query(Student).filter_by(auth_expert=authed).slice(start, start+num_per_page).all()

    url_prefix = request.url
    import re
    if re.match('.*/\d{1,10}$', url_prefix):
        url_prefix = url_prefix[ : url_prefix.rfind('/') ]

    return {
        'persons': persons,
        'total_count': count,
        'total_page': count/ num_per_page + 1,
        'page_index': page_index,
        'url_prefix': url_prefix
    }


@view_config(route_name='admin_persons', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons_page', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons', renderer='json',permission='view',xhr=True)
def view_all_persons(request):

    page = int(request.matchdict.get('page',1) )

    return view_persons(request, page, 10)


@view_config(route_name='admin_persons_authed', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons_authed_page', renderer='admin/persons.jinja2',permission='view')
@wrap_user2
def view_persons_authed(request):
    page = int(request.matchdict.get('page',1) )
    return view_persons_by_auth(request, page, 10, Student.AUTH_STATUS_AUTHED)

@view_config(route_name='admin_persons_unauth', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons_unauth_page', renderer='admin/persons.jinja2',permission='view')
@wrap_user2
def view_persons_unauth(request):
    page = int(request.matchdict.get('page',1) )
    return view_persons_by_auth(request, page, 10, Student.AUTH_STATUS_UNAUTH)

@view_config(route_name='admin_persons_authfail', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons_authfail_page', renderer='admin/persons.jinja2',permission='view')
@wrap_user2
def view_persons_authfail(request):
    page = int(request.matchdict.get('page',1) )
    return view_persons_by_auth(request, page, 10, Student.AUTH_STATUS_FAIL)


@view_config(route_name='admin_persons_reqauth', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons_reqauth_page', renderer='admin/persons.jinja2',permission='view')
@wrap_user2
def view_persons_reqauth(request):
    page = int(request.matchdict.get('page',1) )
    return view_persons_by_auth(request, page, 10, Student.AUTH_STATUS_REQ_FOR_AUTH)

@view_config(route_name='admin_persons_reqexpertauth', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons_reqexpertauth_page', renderer='admin/persons.jinja2',permission='view')
@wrap_user2
def view_persons_reqexpertauth(request):
    page = int(request.matchdict.get('page',1) )
    return view_persons_by_expert_auth(request, page, 10, Student.AUTH_STATUS_REQ_FOR_AUTH)


def includeme(config):



    config.add_route('admin_persons','/admin/persons')
    config.add_route('admin_persons_page','/admin/persons/page/{page}')


    config.add_route('admin_persons_authed',  '/admin/persons/authed')
    config.add_route('admin_persons_authed_page',  '/admin/persons/authed/{page}')

    config.add_route('admin_persons_unauth',  '/admin/persons/unauth')
    config.add_route('admin_persons_unauth_page',  '/admin/persons/unauth/{page}')

    config.add_route('admin_persons_authfail',  '/admin/persons/authfail')
    config.add_route('admin_persons_authfail_page',  '/admin/persons/authfail/{page}')

    config.add_route('admin_persons_reqauth',  '/admin/persons/reqauth')
    config.add_route('admin_persons_reqauth_page',  '/admin/persons/reqauth/{page}')

    config.add_route('admin_persons_reqexpertauth',  '/admin/persons/reqexpertauth')
    config.add_route('admin_persons_reqexpertauth_page',  '/admin/persons/reqexpertauth/{page}')


    # config.add_route('admin_persons_banned',  '/admin/persons/banned')
    # config.add_route('admin_persons_banned_page',  '/admin/persons/banned/{page}')


    config.scan(__name__)
