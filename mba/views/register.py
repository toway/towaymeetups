#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'


import deform
import re
from datetime import datetime
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
from pyramid.security import remember

from kotti import get_settings
from kotti.security import get_principals
from kotti.views.users import deferred_email_validator
from mba import _

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

class RegisterSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title=_(u'姓名'),
        validator=colander.All(name_pattern_validator, name_new_validator)
    )
    email = colander.SchemaNode(
        colander.String(),
        title=_(u'邮箱'),
        validator=deferred_email_validator,
    )
    password = colander.SchemaNode(
        colander.String(),
        title=_(u'密码'),
        validator=colander.Length(min=5),
        widget=deform.widget.PasswordWidget(),
        )

def add_user_success(request, appstruct):
    _massage_groups_in(appstruct)
    name = appstruct['name'] = appstruct['name'].lower()
    appstruct['email'] = appstruct['email'] and appstruct['email'].lower()
    appstruct['last_login_date'] = datetime.now()
    get_principals()[name] = appstruct
    user = get_principals()[name]
    user.password = get_principals().hash_password(appstruct['password'])
    headers = remember(request, user.name)
    success_msg = _(
        'Congratulations! You are successfully registered. '
        'You should be receiving an email with a link to set your '
        'password. Doing so will activate your account.'
        )
    request.session.flash(success_msg, 'success')
    return HTTPFound(location=request.application_url, headers=headers)

@view_config(route_name='register',renderer='register.jinja2')
def view_register(context, request):
    schema = RegisterSchema().bind(request=request)
    form = deform.Form(schema, buttons=[deform.form.Button(u'register', title=u'注册')] )
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

    return {'form': jinja2.Markup(rendered_form)}

def includeme(config):

    settings = config.get_settings()

    config.add_route('register','/register')
    config.scan(__name__)
