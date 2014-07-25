#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, TextInputWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode

from mba.resources import get_act_root
from mba.resources import MbaUser, Act
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.fanstatic import city_css
from mba.views.widget import URLInputWidget
from mba.views.view import MbaTemplateAPI
from mba import _

