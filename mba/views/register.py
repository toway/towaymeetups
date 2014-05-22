#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

import time

import deform
import re
from datetime import datetime
from deform import Button
from deform import Form
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from deform.widget import HiddenWidget

import pyramid

import colander
import jinja2
from deform import ValidationFailure
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.settings import asbool
from pyramid.security import remember

from kotti import get_settings
from kotti.security import get_user

from kotti import DBSession
from kotti.security import get_principals
from kotti.views.users import deferred_email_validator
from mba import _
from mba.views.form import FormCustom
from mba.security import get_student
from mba.resources import MbaUser,Student

# TODO groups for mba
def _massage_groups_in(appstruct):
    groups = appstruct.get('groups', [])
    all_groups = list(appstruct.get('roles', [])) + [
        u'group:%s' % g for g in groups if g]
    if 'roles' in appstruct:
        del appstruct['roles']
    appstruct['groups'] = all_groups

def name_pattern_validator(node, value):
    valid_pattern = re.compile(ur"^[a-zA-Z0-9\u4e00-\u9fa5_\-\.]+$")
    if not valid_pattern.match(value):
        raise colander.Invalid(node, _(u"Invalid value"))

def name_new_validator(node, value):
    if get_principals().get(value.lower()) is not None:
        raise colander.Invalid(
            node, _(u"A user with that name already exists."))

def confirm_password_validator(node, value):
    print node


class RegisterSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title=_(u'用户名'),
        description=_(u'登陆用的唯一用户名'),
        validator=colander.All(name_pattern_validator, name_new_validator)
    )
    email = colander.SchemaNode(
        colander.String(),
        title=_(u'邮箱'),
        description=_(u'请正确填写以便验证'),
        # validator=colander.All(colander.Email,deferred_email_validator),TODO: Email validator
        validator = deferred_email_validator
    )
    password = colander.SchemaNode(
        colander.String(),
        title=_(u'密码'),
        validator=colander.Length(min=6),
        widget=deform.widget.PasswordWidget(css_class="form-control"),
        #传递form-control之后不需要在deform_template/下重写password.jinja2, TextInputWidget同理
        )


def add_user_success(request, appstruct):
    _massage_groups_in(appstruct)
    name = appstruct['name'] = appstruct['name'].lower()
    appstruct['email'] = appstruct['email'] and appstruct['email'].lower()
    appstruct['last_login_date'] = datetime.now()
    #get_principals()[name] = appstruct
    stu = MbaUser(**appstruct)
    DBSession.add(stu)
    user = get_principals()[name]
    user.password = get_principals().hash_password(appstruct['password'])
    DBSession.flush()
    headers = remember(request, user.name)
    success_msg = _(
        'Congratulations! You are successfully registered. '
        'You should be receiving an email with a link to set your '
        'password. Doing so will activate your account.'
        )
    request.session.flash(success_msg, 'success')
    return HTTPFound(location=request.application_url + '/register_details', headers=headers)

# Not other good implements
def add_mbauser_to_student(u):
    ''' Add a MbaUser as a Student too, to do this, add this id in table MbaUser to table Student
    '''
    u.__class__ = Student
    u.type = 'student'
    DBSession.execute("insert into students (id) values (%d);" % u.id)
    DBSession.flush()
    #DBSession.expunge_all()
    DBSession.expunge_all()
    #now get the student
    return DBSession.query(MbaUser).get(u.id)

def add_user_details_success(request, appstruct):


    student = add_mbauser_to_student(get_user(request) )
    for (k,v) in appstruct.items():
        setattr(student, k, v)

    #already added
    #DBSession.add(new_student)
    DBSession.flush()

    return student


@view_config(route_name='register',renderer='register.jinja2')
def view_register(context, request):
    schema = RegisterSchema(
            css_class="setup-account",
            title=u'注册帐号').bind(request=request)

    form = deform.Form(schema, buttons=[
                deform.form.Button(u'register',
                                   css_class='btn-primary',
                                   title=u'注册')] )
    rendered_form = None

    if 'register' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()
        else:
            settings = get_settings()

            register_groups = settings['kotti.register.group']
            if register_groups:
                appstruct['groups'] = [register_groups]

            register_roles = settings['kotti.register.role']
            if register_roles:
                appstruct['roles'] = set(['role:' + register_roles])
            return add_user_success(request, appstruct)

    if rendered_form is None:
        rendered_form = form.render(request.params)

    #return {'form': form} #可以在 .jinja2模板中用{{ form['name'].title }}实现retail form rendering,对name控件进行控制
    return {'form': jinja2.Markup(rendered_form)}






class RegisterDetailsSchema(colander.Schema):


    this_year = datetime.today().year
    join_mba_years = [(this_year-i, "%s" % (this_year-i))
                                            for i in range(30) ]
    for i in range(30):
        year = this_year - i
        join_mba_years.append(("%s" % year,"%s" % year))

    school = colander.SchemaNode(
        colander.String(),
        title=_(u'学校名称'),
    )
    school_year = colander.SchemaNode(
        colander.Integer(),
        title=_(u'入学年份'),
        widget=deform.widget.SelectWidget(values=join_mba_years,
                                          css_class='form-control')
    )
    real_name = colander.SchemaNode(
        colander.String(),
        title=_(u'真实姓名'),
    )
    birth_date = colander.SchemaNode(
        colander.Date(),
        title=_(u'出生日期'),
         widget=deform.widget.DateInputWidget(
                            values=join_mba_years,
                            css_class='form-control')

    )
    phone = colander.SchemaNode(
        colander.String(),
        title=_(u'联系电话'),

    )




@view_config(route_name='register_details',renderer='register_details.jinja2')
def view_register_details(context, request):
    schema = RegisterDetailsSchema(
            css_class="setup-account-details",
            title=u'完善信息').bind(request=request)
    '''
    form = FormCustom(schema,
            template='register_details_form',
            buttons=[
                deform.form.Button(u'submit',
                           css_class='btn-primary',
                           title=_(u'提交')),
                deform.form.Button(u'skip',
                           title=_(u'跳过'))
    ])
    '''
    form = deform.Form(schema,
                       buttons=[
                           deform.form.Button('submit', css_class='btn-primary',title=_(u'提交')),
                           deform.form.Button('skip',title=_(u'跳过')),
                       ])
    rendered_form = None


    if 'submit' in request.POST:


        try:
            appstruct = form.validate(request.POST.items())
            student = add_user_details_success(request, appstruct)
            headers = remember(request, student.name)

            # Seems useless, anybody tell what's hell this two lines do?
            # success_msg = _('Congratulations! Successfully registed')
            # request.session.flash(success_msg, 'success')

            return HTTPFound(location=request.application_url + '/register_finish', headers=headers)


        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()

    if 'skip' in request.POST:
        # Just Add a record to table student
        student = add_mbauser_to_student(get_user(request) )
        headers = remember(request, student.name)
        return HTTPFound(location=request.application_url + '/register_finish', headers=headers)


    if rendered_form is None:
        rendered_form = form.render(request.params)
        #rendered_form = form.custom_render(request.params), #raise TypeError: unhashable type: 'NestedMultiDict'



    #return {'form': form} #可以在 .jinja2模板中用{{ form['name'].title }}实现retail form rendering,对name控件进行控制
    return {'form': jinja2.Markup(rendered_form)}

@view_config(route_name='register_finish', renderer='register_finish.jinja2')
def view_register_finish(context, request):
    return {}
    #return pyramid.response.Response("OK")

def includeme(config):

    settings = config.get_settings()

    config.add_route('register','/register')
    config.add_route('register_details','/register_details')
    config.add_route('register_finish','/register_finish')
    config.scan(__name__)
