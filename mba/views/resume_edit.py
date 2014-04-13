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
    			"person_info":  {"real_name":u"杨先生","sex":u"男", "birth_date":u"2009-9-1", 
								  "work_years":u"一到三年", "work_years":u"一到三年",
								  "identify":u"43052119890902", "identify_type":u"身份证","residence":u"深圳市南山区",
								  "email":u"1018556223@qq.com", "salary":u"10000","phone":u"13760107591",
								  "company_phone":u"086-0755-26590234-432"
								  
								 },
				"job_intension":  {"location":u"深圳","position":u"软件工程师", "expect_salary":u"15-25k"},
				"language":  {"language":u"英语,粤语"},
    			"education":	[
    								{"start_date": u"2006-9-1", "finish_date":u"2009-9-1", "school":u"电子科技大学", "major":u"通信工程", "degree":u"研究生"},
    								{"start_date": u"2001-9-1", "finish_date":u"2006-9-1", "school":u"电子科技大学", "major":u"通信工程", "degree":u"本科"}
    							],
    			"experience":	[
    								{"start_date": u"2006-9-1", "finish_date":u"2009-9-1", "company":u"TPLINK", "company_type":u"私营/民营", "scale":u"1000-2000人","location":u"软件工程师"},
    								{"start_date": u"2001-9-1", "finish_date":u"2006-9-1", "company":u"浩宁达", "company_type":u"上市公司", "scale":u"2000-5000人","location":u"软件工程师"}
    							]
    	   }

def includeme(config):
    settings = config.get_settings()
    config.add_route('resume_edit','/resume_edit')
    config.scan(__name__)
