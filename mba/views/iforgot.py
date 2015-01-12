#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'
__date__ = '20150112'
__desc__ = u'忘记密码功能'


import deform
from deform import Button
from deform import Form
from deform import ValidationFailure
from deform.widget import HiddenWidget, TextInputWidget, PasswordWidget

import colander
import jinja2
from pyramid.view import view_config
from pyramid.request import Response
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool
from pyramid.security import forget

from pyramid_deform import FormWizard



from mba import _
from mba.utils import wrap_user as wrap_user2
from mba.utils.decorators import wrap_user
from mba.resources import *
from mba.utils import  validators
from mba.views.register import deferred_phonecode_validator
from mba.views.widget import PhoneValidateCodeInputWidget


def phone_validator(node, value):

    user = DBSession.query(MbaUser).filter_by(phone=value).first()
    if not user :
        raise colander.Invalid(u"未注册的手机号？")


class ForgotPassSchema(colander.MappingSchema):
    title = u"重置密码"
    phone = colander.SchemaNode(
        colander.String(),
        title=_(u"手机号"),
        description=_(u"请输入注册时的手机号"),
        validator=colander.All(validators.PhoneNum(), phone_validator),
        #missing = None, #u"",
        # widget=TextInputWidget()
    )

    sms_validate_code = colander.SchemaNode(
        colander.String(10),
        title=_(u"验证码"),
        validator=deferred_phonecode_validator,
        widget=PhoneValidateCodeInputWidget(inputname='phone')
    )

class ResetPassSchema(colander.MappingSchema):

    title = u"重置密码"

    newpsw = colander.SchemaNode(
        colander.String(),
        title=_(u"新密码："),
        validator=validators.password_pattern_validator
    )



def reset_password_done(request, state):

    phone = state[0]['phone']
    newpw = state[1]['newpsw']

    user = DBSession.query(MbaUser).filter_by(phone=phone).first()
    if user:
        user.password = get_principals().hash_password(newpw)

        # headers = forget(request)

        return Response("重置成功！ <a href='/login'>重新登陆?</a>")


    return Response("重置失败！ 不存在的手机号")



@view_config(route_name='iforgot', renderer="iforgot.jinja2")
def view_iforgot(request):
    a = FormWizard("iforgot", reset_password_done, ForgotPassSchema(), ResetPassSchema())
    return a(request)





def includeme(config):
    settings = config.get_settings()
    config.add_route('iforgot','/iforgot')
    config.scan(__name__)
