#!/usr/bin/python
# coding: utf-8


__author__ = 'ycf'


import deform
from deform import Button
from deform import Form
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from deform.widget import HiddenWidget

import colander
import jinja2
from deform import ValidationFailure

from sqlalchemy.sql.expression import and_

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool
from pyramid.response import Response

from js.jquery import jquery
from js.jqueryui import jqueryui
from js.jquery_form import jquery_form

from kotti import get_settings
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from kotti import DBSession
from kotti.security import get_user

from mba import _
from mba.utils import wrap_user, RetDict
from mba.resources import Student, Position, MbaUser, friend


def integers(*segment_names):
    def predicate(context, request):
        match = request.matchdict
        for segment_name in segment_names:
            try:
                match[segment_name] = int(match[segment_name])
            except (TypeError, ValueError):
                return False
        return True
    return predicate

person_id_predic = integers("id")

class PersonInfoWidget(object):
    renderer = staticmethod(deform.Form.default_renderer)
    def __init__(self, user):
        self.user = user
        self.template = 'person_form.jinja2'

    def render(self):
        #TODO do better
        ss = [u'company', u'industry', u'special_skill', u'interest', u'between', u'introduction', u'location']
        u = self.user
        for s in ss:
            if not getattr(u,s):
                setattr(u, s, u"")
        return self.renderer(self.template, person_info=self.user)

@view_config(route_name='person', renderer='person.jinja2', custom_predicates=(person_id_predic,),permission='view')
def view_person(request):
    jquery.need()
    jqueryui.need()
    jquery_form.need()


    curr_user = get_user(request)
    if not curr_user:
        return HTTPFound(location="/login?came_from=%s" % request.url)

    if "hd_id" in request.POST:
        try:
            post = request.POST
            userid = int(post['hd_id'])
            user = DBSession.query(Student).get(userid)
            if curr_user.id != user.id:
                return Response("ERROR")
            #user.email = post['email']
            user.phone = post['phone']
            user.company = post['company']
            user.industry = post['industry']
            user.location = post['location']
            user.school = post['school']
            user.special_skill = post['special_skill']
            user.interest = post['interest']
            user.between = post['between']
            user.introduction = post['introduction']
            user.real_name = post['title']
            person_info_widget = PersonInfoWidget(user)
            return Response(person_info_widget.render())
        except:
            return Response("ERROR")
    
    userid = int(request.matchdict['id'])
    user = DBSession.query(Student).get(userid)
    new_positions = DBSession.query(Position).all()[0:8]
    person_info_widget = PersonInfoWidget(user)
    toknown_list = DBSession.query(Student).filter(Student.id != curr_user.id)[0:8]
    user_status = 0
    if curr_user.id == user.id:
        user_status = 1
    else:
        user.add_visit(curr_user)
        if user in curr_user.all_friends:
            user_status = 2

    return wrap_user(request, {
                "person_info": user,
                "user_status": user_status,
                "curr_id": curr_user.id,
                "resumes": user.resumes,
                "visitors": user.visitors[0:8],
                "visit_count": len(user.visitors),
                "new_positions": new_positions,
                "person_info_form": person_info_widget.render(),
                "toknown_list": toknown_list,
           })




@view_config(route_name='friend_set')
def friend_set(request):
    curr_user = get_user(request)
    id1 = int(request.matchdict['id1'])
    id2 = int(request.matchdict['id2'])
    id3 = int(request.matchdict['id3'])
    if (not curr_user) or (curr_user.id != id1) or id1 == id2:
        return Response("1")
    else:
        is_error = False
        u2 = DBSession.query(Student).filter(Student.id == id2).one()
        if not u2:
            return Response("1")
        if id3 > 0 and u2 not in curr_user.friends:
            try:
                curr_user.friends.append(u2)
            except:
                is_error = True
        if id3 <= 0 and u2 in curr_user.friends:
            try:
                curr_user.friends.remove(u2)
            except:
                is_error = True
        if is_error:
            return Response("1")
        else:
            return Response("0")

@view_config(route_name='ajax_friends', renderer='json', xhr=True)
def ajax_friends(request):

    #return dict(retval='ok',SUCCESS=0,errcode=0)
    #return RetDict(retval="OK")

    cur_user = get_user(request)
    if not cur_user:
        return RetDict(errcode=RetDict.ERR_CODE_NOT_LOGIN)

    method = request.POST.get('method', None)

    if not method or method not in ['add_friend','cancel_friend','agree_friend']:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)



    target_person_id = request.POST.get('target-person', None)

    if not target_person_id :
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    target_person = DBSession.query(MbaUser).filter_by(id=target_person_id).first()

    if target_person in cur_user.all_friends:
        return RetDict(errmsg=u"已经是朋友")

    elif target_person in cur_user.my_requests:
        return RetDict(errmsg=u"等待对方通过")

    elif target_person in cur_user.others_requests:
        # Impossible in front-end , but we did in backend
        relation= DBSession.query(friend).filter(
            and_(
                friend.c.user_a_id==target_person_id,
                friend.c.user_b_id==cur_user.id)
            ).one()

        relation.status = 1 # It seems does not work


        return RetDict(retval=u"同意对方加友请求")

    else: # We add frined now
        # new_friend_relationship = friend(user_a_id=cur_user.id,
        #        user_b_id=target_person_id)
        cur_user.friendship.append(target_person)
        #target_person.others_requests.append(cur_user)
        #DBSession.commit()

        return RetDict(retval=u"已经申请加为好友，等待对方同意")









def includeme(config):
    config.add_route('person','/person/{id}')
    config.add_route('ajax_friends', '/friends')
    config.add_route('friend_set','/friend_set/{id1:\d+}/{id2:\d+}/{id3:\d+}')
    config.scan(__name__)
