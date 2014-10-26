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
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import MbaUser, Student

__author__ = 'sunset'
__date__ = '20140909'
__description__ = u'用户管理'


from js.jquery import jquery



def view_persons(request, page_index=1, num_per_page=10):
    jquery.need()

    #TODO: Do I need to judge if the user is logged in here?
    if 'method' in request.POST:

        try:
            method = request.POST['method'] # pass-iauth, cancel-iauth, fail-iauth
            personid = request.POST['person-id']

            person = DBSession.query(MbaUser).filter_by(id=personid).first()
            if not person :
                raise Exception(u"没有该用户!")

            # 0, unauthed, 1 authed, 2 authfail, ( 3 request for auth?)
            if method == 'pass-iauth':
                person.auth_info = 1
                request.session.flash(u"用户'%s'认证成功" % (person.real_name or person.name) , 'success' )

            elif method == 'cancel-iauth':
                person.auth_info = 0
                request.session.flash(u"用户'%s'取消认证成功" % (person.real_name or person.name) , 'success' )

            elif method == 'fail-iauth':
                person.auth_info = 2
                request.session.flash(u"用户'%s'不通过认证成功" % (person.real_name or person.name) , 'success' )


        except Exception,ex:
            err_msg = "%s" % ex
            request.session.flash(_(u"错误：'%s'" % err_msg), 'error')

        finally:
            return {}



    start = (page_index-1) * num_per_page
    count = DBSession.query(MbaUser).count()
    persons = DBSession.query(MbaUser).slice(start, num_per_page).all()



    return wrap_user(request, {
        'persons': persons,
        'total_count': count,
        'total_page': count/ num_per_page + 1,
        'page_index': page_index
    })

def view_persons_by_auth(page_index=1, num_per_page=10, authed=0):
    jquery.need()

    start = (page_index-1) * num_per_page

    count = DBSession.query(Student).filter_by(auth_info=authed).count()
    persons = DBSession.query(Student).filter_by(auth_info=authed).slice(start, num_per_page).all()


    return {
        'persons': persons,
        'total_count': count,
        'total_page': count/ num_per_page + 1,
        'page_index': page_index
    }


@view_config(route_name='admin_persons', renderer='admin/persons.jinja2',permission='view')
@view_config(route_name='admin_persons', renderer='json',permission='view',xhr=True)
def view_all_persons(request):
    return view_persons(request, 1, 10)


@view_config(route_name='admin_persons_auth', renderer='admin/persons.jinja2',permission='view')
@wrap_user2
def view_persons_auth(request):
    return view_persons_by_auth(1, 10, 0)


def includeme(config):



    config.add_route('admin_persons','/admin/persons')
    config.add_route('admin_persons_auth',  '/admin/persons/unauth')



    config.scan(__name__)
