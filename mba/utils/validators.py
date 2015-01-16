#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'
__date__ = '20150112'
__desc__ = u'验证器'

import re

import colander
from colander import Regex, text_

from kotti.security import DBSession, get_principals

from mba import _
from mba.resources import InvitationCode



class PhoneNum(Regex):
    """ Phone num validator. If ``msg`` is supplied, it will be
        the error message to be used when raising :exc:`colander.Invalid`;
        otherwise, defaults to 'Invalid email address'.
    """
    def __init__(self, msg=None):
        if msg is None:
            msg = _("Invalid phone number")
        super(PhoneNum, self).__init__(
            text_('^\d{11}$'), msg=msg)




def password_pattern_validator(node, value):
    if not value or len(value.strip()) < 8:
        raise colander.Invalid(node, _(u"密码至少8位") )




@colander.deferred
def deferred_phonecode_validator(node, kw):
    def phonecode_validator(node, value):
        if not value or value != kw['request'].session.get('sms_validate_code',None):
            raise colander.Invalid(node,
                                   _(u'验证码不对哟！'))
    return phonecode_validator


def name_pattern_validator(node, value):
    valid_pattern = re.compile(ur"^[a-zA-Z0-9\u4e00-\u9fa5_\-\.]+$")
    if not valid_pattern.match(value):
        raise colander.Invalid(node, _(u"Invalid value"))

def name_new_validator(node, value):
    if get_principals().get(value.lower()) is not None:
        raise colander.Invalid(
            node, _(u"A user with that name already exists."))

def realname_pattern_validator(node, value):
    if value is None or len(value.strip())==0:
        raise colander.Invalid(
            node, _(u"不合法的姓名"))

def invitation_code_validator(node, value):
    # print 'invitation_code_validator:', value
    if not value or \
            DBSession.query(InvitationCode)\
                    .filter_by(code=value, status=InvitationCode.AVAILABLE).first() is None:
        raise  colander.Invalid(
            node, _(u"邀请码不存在或已经失效"))