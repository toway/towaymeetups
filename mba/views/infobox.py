#!/usr/bin/python
# coding: utf-8

__author__ = 'sunset'
__date__ = "20141026"

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from js.jquery import jquery

from kotti import DBSession
from kotti.security import get_user

from sqlalchemy import or_, and_

from mba.utils.decorators import wrap_user
from mba.utils import RetDict
from mba.resources import Message, MbaUser




def get_messages(type, context, request):
    jquery.need()

    cur_user = get_user(request)

    if not cur_user:
        return HTTPFound(location="/login?came_from=%s" % request.url)

    messages = []

    if type == 'all_messages':
        messages = DBSession.query(Message).filter_by(reciever_id=cur_user.id).all()
    elif type == 'system_messages':
        messages = DBSession.query(Message).filter(
            and_(
                Message.reciever_id==cur_user.id,
                or_(Message.type==0 ,
                    Message.type==1 ,
                    Message.type==10)
            )).all()
    elif type == 'friend_messages':
        messages = DBSession.query(Message).filter_by(reciever_id=cur_user.id, type=2).all()

    elif type == 'view_invitation_person':
        messages = DBSession.query(Message).filter_by(reciever_id=cur_user.id, type=11).all()


    return {'type': type, 'messages': messages}


@view_config(route_name="infobox_m", renderer='infobox.jinja2')
@wrap_user
def view_infobox_m(context, request):
    return get_messages('all_messages', context, request)



@view_config(route_name="infobox_mf", renderer='infobox.jinja2')
@wrap_user
def view_infobox_mf(context, request):
    return get_messages('friend_messages', context, request)


@view_config(route_name="infobox_ms", renderer='infobox.jinja2')
@wrap_user
def view_infobox_ms(context, request):
    return get_messages('system_messages', context, request)



@view_config(route_name="infobox_ip", renderer='infobox.jinja2')
@wrap_user
def view_infobox_ms(context, request):
    return get_messages('view_invitation_person', context, request)







def prompt_friend(cur_user, context, request):
    try:
        invitee_list = [ int(i) for i in request.POST.getall('invitee_list[]')  ]
    except ValueError,ve:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)
    if not invitee_list or len(invitee_list) ==  0:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


    try:
        prompted_userid = int(request.POST.get('prompted_userid',None) )
    except ValueError,ve:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)
    if prompted_userid is None:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


    prompted_user = DBSession.query(MbaUser).filter_by(id=prompted_userid).one()

    if not prompted_user:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    #### TODO 注意,这里要防止SQL注入
    extramsg = request.POST.get('extramsg','')


    content = u" <a href='/person/%d'>%s</a> 向你推荐朋友 <a href='/person/%d'>%s</a>, " \
              u" 并说:%s <a href='/person/%d'>去看看Ta</a>?" \
                % (cur_user.id,
                   cur_user.real_name or cur_user.name,
                   prompted_userid,
                   prompted_user.real_name or prompted_user.name,
                   extramsg,
                   prompted_userid)
    for invitee in invitee_list:
        invitation = Message(sender_id=cur_user.id,
                             reciever_id=invitee,
                             type=11,
                             content=content)
        DBSession.add(invitation)

    friend = DBSession.query(MbaUser).filter_by(id=invitee_list[0]).one()
    content = u" <a href='/person/%d'>%s</a> 向朋友 <a href='/person/%d>%s</a>等, 推荐了你" \
                % (cur_user.id,
                   cur_user.real_name or cur_user.name,
                   friend.id,
                   friend.real_name or friend.name
                 )
    invitation = Message(sender_id=cur_user.id,
                             reciever_id=prompted_userid,
                             type=11,
                             content=content)
    DBSession.add(invitation)


    DBSession.flush()

    msg = u"已向朋友推荐"
    return RetDict(retval=msg)


def mark_msg_read(cur_user, context, request):

    try:
        msgid = request.POST.get('msgid',0)
    except ValueError, ve:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)
    if msgid == 0:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    msg = DBSession.query(Message).filter_by(id=msgid).one()
    if msg:
        msg.status = 1 # 1 read

    return RetDict(retval=u"成功标记为已读")


@view_config(route_name='api_infobox', renderer='json', xhr=True, request_method="POST")
def api_infobox(context, request):

    PROMPT_FRIEND = 'prompt_friend' #推荐好友给好友
    MARK_AS_READ = 'mark_as_read'




    cur_user = get_user(request)
    if not cur_user:
        return RetDict(errcode=RetDict.ERR_CODE_NOT_LOGIN)

    if not request.POST :
        return {}

    method = request.POST.get('method',None)

    if method not in [PROMPT_FRIEND, MARK_AS_READ]:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    if method == PROMPT_FRIEND:
        return prompt_friend(cur_user, context, request)
    elif method == MARK_AS_READ:
        return mark_msg_read(cur_user, context, request)



    return {}






def includeme(config):

    #config.add_route('infobox', '/infobox')
    config.add_route('infobox_m', '/infobox/messages')
    config.add_route('infobox_ms', '/infobox/messages/system')
    config.add_route('infobox_mf', '/infobox/messages/friend')
    # config.add_route('infobox_im', '/infobox/invitations/meetup')
    config.add_route('infobox_ip', '/infobox/invitations/person')

    config.add_route('api_infobox','/api/infobox')

    config.scan(__name__)
