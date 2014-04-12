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
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool

from kotti import get_settings
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from js.jquery import jquery
from js.jqueryui import jqueryui
from js.jquery_form import jquery_form
from js.deform import deform_js
from js.jquery_timepicker_addon import timepicker
from js.deform_bootstrap import ui_bootstrap_theme

from mba import _

@view_config(route_name='resume_edit',renderer='resume_edit.jinja2')
def view_job(request):
    jquery.need()
    jqueryui.need()
    jquery_form.need()
    #deform_js.need()
    timepicker.need()
    ui_bootstrap_theme.need()
    return {
    		"test":"test",
    			"education":	[
    								{"start_date": u"2006-9-1", "finish_date":u"2009-9-1", "school":u"电子科技大学", "major":u"通信工程", "degree":u"研究生"},
    								{"start_date": u"2001-9-1", "finish_date":u"2006-9-1", "school":u"电子科技大学", "major":u"通信工程", "degree":u"本科"}
    							]
    	   }

def includeme(config):
    settings = config.get_settings()
    config.add_route('resume_edit','/resume_edit')
    config.scan(__name__)
