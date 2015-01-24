#!/usr/bin/python
# coding: utf-8

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, HiddenWidget
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
from kotti.views.form import AddFormView, EditFormView


from mba import _
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import Banner
from mba.views.widget import ImageUploadWidget2

from js import fineuploader
from js.jquery import jquery


from mba.utils import RetDict
from mba.resources import Act, Participate, MbaUser

__author__ = 'sunset'
__date__ = '20150113'
__desc__ = u'活动参与者'



@view_config(route_name="admin_meetup_particinpate", renderer='/admin/meetup_particinpates.jinja2')
@wrap_user
def admin_meetup_particinpate_view(context, request):
    id = request.matchdict['id']
    meetup = DBSession.query(Act).get(id)

    if meetup is None:
        return Response(u"不存在的活动")

    if 'delete' in request.POST:
        # 取消选中的人参加活动
        todel = request.POST.getall('participate_check')

        principals = get_principals()
        for mid in todel:

            # print 'mid:%s, len mid:%d'% ( mid, len(mid) )

            to_cancel_user = principals.get(int(mid))
            # if to_cancel_user in meetup.parts:
                # meetup.parts.remove(to_cancel_user)



            enrolled_user = DBSession.query(Participate).filter_by(user_id=int(mid), act_id=meetup.id).first()
            if enrolled_user is not None :
                # print meetup

                DBSession.delete(enrolled_user)
                request.session.flash(u"已取消选中人报名活动!" , 'success')
                DBSession.flush()
    elif 'approve_meetup_auth'  in request.POST:
        # 添加活动认识

        toauth = request.POST.getall('participate_check')


        for mid in toauth:

            to_auth_user = DBSession.query(MbaUser).filter_by(id=mid).first()

            print to_auth_user

            if to_auth_user is not None:
                to_auth_user.auth_meetup = True

                request.session.flash(u"已成功给‘%s’添加活动认证" % to_auth_user.real_name , 'success')

                DBSession.flush()

    jquery.need()

    return {'meetup': meetup}


def includeme(config):


    config.add_route('admin_meetup_particinpate',  '/admin/meetup/{id}/particinpate')

