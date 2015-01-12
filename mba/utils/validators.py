#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'
__date__ = '20150112'
__desc__ = u'验证器'


import colander
from colander import Regex, text_
from mba import _




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