#/usr/bin/python
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
from mba.resources import Act, Review, InvitationCode

__author__ = 'sunset'
__date__ = '20141218'



@view_config(route_name='my_invitationcode', renderer='i_invitationcode.jinja2')
@wrap_user
def view_my_meetups(context, request):
    user = get_user(request)

    generated = DBSession.query(InvitationCode).filter_by(sender_id=user.id).all()
    if not generated:


        # TODO: 根据用户组的权限生成相应数量的注册码，暂时为10个

        # print user.groups
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


    return {'invitationcode': generated}

def includeme(config):
    config.add_route('my_invitationcode','/i/invitationcode')

    config.scan(__name__)