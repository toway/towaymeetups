#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

import pyramid
from pyramid.view import view_config

from mba import _

@view_config(route_name='activity', renderer='activity.jinja2')
def view_register_finish(context, request):

    resp_dict = {
        'status': 1,# 1=ON_GOING/0=FINISHED
        'status_desc': u'正在进行中...',
        'title':u'人格解析与信任建立',
        'abstract':u'简介',
        'content':u'活动介绍',
        'tips':u'xxxxx',
        'speaker':u'李玫瑾',
        'speaker_introduction':u'李玫瑾，系中国人民公安大学教授，研究生导师。中国警察协会学术委员，中国青少年犯罪研究会副会长，中国心理学会法心理学专业委员会副主任等。',
        'comments':[u'ok',u'ok2'],
        'applicants':[u'陈...',u'余争'] * 10
    }

    return resp_dict

@view_config(route_name="find", renderer='find.jinja2')
def view_find(context, request):
    return {'aaa':'bbb'}

def includeme(config):

    config.add_route('activity','/activity')
    config.add_route('find','/find')
    config.scan(__name__)

