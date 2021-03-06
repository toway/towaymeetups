#!/usr/bin/python
# coding: utf-8

__author__ = 'sunset'

from pyramid.view import view_config
from js.jquery import jquery

from kotti import DBSession
from kotti.security import get_user


from mba.utils.decorators import wrap_user
from mba.utils import RetDict
from mba.resources import MeetupInvitation, InvitationCode

## This file is abandoned now@@@!!!! by sunset 2014.12.18

@view_config(route_name="invitations", renderer='invitations.jinja2')
@wrap_user
def view_invatation(context, request):
    jquery.need()
    ret = {}
    if request.matchdict['type'] == 'meetup':
        # 活动邀请
        ret['type']  = 'meetup'


    elif request.matchdict['type'] == 'person':
        # 人脉邀请
        ret['type']  = 'person'

    elif request.matchdict['type'] == 'code':
        # 注册邀请码
        user = get_user(request)

        generated = DBSession.query(InvitationCode).filter_by(sender_id=user.id).all()
        if not generated:


            # TODO: 根据用户组的权限生成相应数量的注册码，暂时为10个

            print user.groups
            count = 10
            toadd = []

            import hashlib
            import datetime
            def generate_invitation_code(ii):
                # TODO: Fuck! I don't care about the code collision right now!
                code = str(user.id * 100 + ii)
                strcode = hashlib.md5(code).hexdigest()

                return strcode[:6].upper()


            now = datetime.datetime.now(tz=None)
            for i in range(count):
                code = generate_invitation_code(i)

                expiration = now + datetime.timedelta(days = 7*(i+1))
                toadd.append( InvitationCode(code=code,
                                             sender_id=user.id,
                                             receiver_id=None,
                                             expiration=expiration
                                             ) )

            DBSession.add_all(toadd)
            DBSession.flush()



            generated = DBSession.query(InvitationCode).filter_by(sender_id=user.id).all()


        ret['invitation_code'] = generated






        ret['type'] = 'code'



    return ret


def mark_meetup_invitation(cur_user, context, request):
    try:
        invitation_id  = int(request.POST.get( 'invitation_id', 0))
    except ValueError,ve:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)
    if  invitation_id==0:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    invitation = DBSession.query(MeetupInvitation).filter_by(id=invitation_id).first()
    if invitation:
        invitation.status = 1 # 0 : unread, 1: ignore 2:accept, 3: reject 4: deleted

        return RetDict(retval=u"成功无视掉邀请")

    return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)



def invite_friend(cur_user, context, request):
    try:
        meetup_id  = int(request.POST.get( 'meetup_id', 0))
    except ValueError,ve:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    if  meetup_id==0:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


    try:
        invitee_list = [ int(i) for i in request.POST.getall('invitee_list[]')  ]

    except ValueError,ve:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


    appended = []
    for invitee in invitee_list:
        if isinstance(invitee, int):
            appended.append(invitee)

    # If change to MySQL, id will be autoincrement and unneeded.
    lastrecord = DBSession.query(MeetupInvitation).order_by(MeetupInvitation.id.desc()).first()
    if lastrecord:
        lastrecord = lastrecord.id
    else:
        lastrecord = 0

    idx = 1

    for invitee in appended:
        invitation = MeetupInvitation(id=lastrecord+idx,
                                      inviter_id=cur_user.id,
                                      invitee_id=invitee,
                                      meetup_id=meetup_id)
        DBSession.add(invitation)
        idx += 1

    DBSession.flush()

    return RetDict(retval=u"成功添加邀请")

def api_meetup_invitation(cur_user, context, request):
    method = request.POST.get('method', None)

    if method not in ['invite','mark_invitation']:
        return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

    if method == 'invite':
        return invite_friend(cur_user, context, request)
    else:
        return mark_meetup_invitation(cur_user, context, request)





@view_config(route_name='ajax_api_invitations', renderer='json', xhr=True, request_method="POST")
def ajax_invitation(context, request):

    cur_user = get_user(request)
    if not cur_user:
        return RetDict(errcode=RetDict.ERR_CODE_NOT_LOGIN)

    if request.POST :
        type = request.POST.get('type',None)
        if type == 'meetup':
            return api_meetup_invitation(cur_user, context, request)
        elif type == 'person':
            pass



    return {}






def includeme(config):

    config.add_route('invitations', '/invitations/{type}')

    config.add_route('ajax_api_invitations','/api/invitations')

    config.scan(__name__)
