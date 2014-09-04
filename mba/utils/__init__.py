#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

from datetime import datetime

import random

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
import kotti
from kotti import get_settings
from kotti.security import get_user



DEFULT_AVATARS_COUNT_COLLETED = 2

def assign_default_avatar(user):

    # assign a random avatar
    # Currently, I only collect 2 default avatars
    avatar_index = int(random.random() * DEFULT_AVATARS_COUNT_COLLETED)
    user.avatar = "%s/default_avatar_%d.png" % (
                                                   get_settings()['mba.avatar_prefix'] ,
                                                   avatar_index)

    return user

def wrap_user(request, ret_dict_to_update):
    user = get_user(request)


    ret_dict_to_update.update({'user':user})

    return ret_dict_to_update