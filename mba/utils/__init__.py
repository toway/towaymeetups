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
from kotti.security import get_user

DEFULT_AVATARS_COUNT_COLLETED = 2

def wrap_user(request, ret_dict_to_update):
    user = get_user(request)

    if user is not None:
        if user.avatar is None:
            # assign a random avatar
            # Currently, I only collect 2 default avatars
            avatar_index = int(random.random() * DEFULT_AVATARS_COUNT_COLLETED)
            user.avatar = "default_avatar_%d.png" % avatar_index

        # user.avatar_prefix = kotti.get_settings()['mba.avatar_prefix']

    ret_dict_to_update.update({'user':user})

    return ret_dict_to_update