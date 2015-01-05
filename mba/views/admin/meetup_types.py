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
#from mba.utils.decorators import wrap_user
from mba.utils import wrap_user
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import MeetupType

__author__ = 'sunset'
__date__ = '20140904'
__description__ = u'活动类别管理'


from js.jquery import jquery



@view_config(route_name='admin_meetup_types', renderer='admin/meetup_types.jinja2',permission='view')
@view_config(route_name='admin_meetup_types', renderer='json',permission='view',xhr=True)
def view_meetup_types(context, request):
    jquery.need()

    user = get_user(request)
    if not user:
        return HTTPFound(location="/login?came_from=%s" % request.url)


    err_msg = u""

    if 'method' in request.POST:
        # mt stands for meetup-type
        try:
            method = request.POST['method'] # add-mt, del-mt, mdf-mt

            if method  == 'add-mt':

                new_type_title = request.POST['mt-title']
                DBSession.add( MeetupType(title=new_type_title))
                request.session.flash((u"成功添加：'%s'" % new_type_title), 'success')
            else:

                mt_id = int(request.POST['mt-id'])
                to_op_mt = DBSession.query(MeetupType).filter_by(id=mt_id).first()

                mt_title =  request.POST['mt-title']

                if not to_op_mt:
                    raise Exception(u"错误的参数")

                if method == 'del-mt':
                    DBSession.delete(to_op_mt)
                    request.session.flash(_(u"成功删除'%s'" % mt_title), 'success')

                elif method == 'mdf-mt':
                    to_op_mt.title = mt_title
                    request.session.flash(_(u"修改成功!"), 'success')

                else:
                    err_msg = u"错误的方法"
                    request.session.flash(_(u"错误的参数"))

        except Exception,ex:
            err_msg = "%s" % ex
            request.session.flash(_(u"错误：'%s'" % err_msg), 'danger')


        finally:
            return {}




    queried = DBSession.query(MeetupType)
    count = DBSession.query(MeetupType).count()


    return wrap_user(request, {'meetup_types': queried,'count': count } )



def includeme(config):


    config.add_route('admin_meetup_types','/admin/meetups/types')

    config.scan(__name__)
