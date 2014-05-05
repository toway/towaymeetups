#!/usr/bin/python
# coding: utf-8

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user
from mba.resources import MbaUser
from mba import _

@view_config(route_name='home', renderer='index2.jinja2')
def view_home(request):
    #only for test
    stu = DBSession.query(MbaUser).filter_by(email='a@gmail.com').first()
    headers = remember(request, stu.name)
    response = render_to_response('index2.jinja2', {'project':'lession2'}, request=request)
    response.headerlist.extend(headers)
    return response

@view_config(route_name='permission', renderer='index.jinja2', permission='admin')
def view_permission(request):
    return {'project': 'lesson2'}

class LoginSchema(colander.Schema):
    email = colander.SchemaNode(
        colander.String(),
        title=_(u'邮箱'),
        validator=colander.Email(),
    )
    password = colander.SchemaNode(
        colander.String(),
        title=_(u'密码'),
        validator=colander.Length(min=5),
        widget=deform.widget.PasswordWidget(),
        )

def _find_user(login):
    principals = get_principals()
    principal = principals.get(login)
    if principal is not None:
        return principal
    else:
        try:
            Email().to_python(login)
        except Exception:
            pass
        else:
            for p in principals.search(email=login):
                return p

@view_config(name='login', renderer='register.jinja2')
def login(context, request):
    schema = LoginSchema().bind(request=request)
    form = deform.Form(schema, buttons=[deform.form.Button(u'submit', title=u'登录')] )
    rendered_form = None

    principals = get_principals()
    came_from = request.params.get(
        'came_from', request.resource_url(context))
    login, password = u'', u''

    if 'submit' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()
        user = _find_user(appstruct['email'])
        if (user is not None and user.active and
                principals.validate_password(appstruct['password'], user.password)):
            headers = remember(request, user.name)
            request.session.flash(
                _(u"Welcome, ${user}!",
                  mapping=dict(user=user.title or user.name)), 'success')
            user.last_login_date = datetime.now()
            if came_from == 'login':
                came_from = '/'
            return HTTPFound(location=came_from, headers=headers)
        request.session.flash(_(u"Login failed."), 'error')

    if rendered_form is None:
        rendered_form = form.render(request.params)

    return {'form': jinja2.Markup(rendered_form)}

def includeme(config):
    #print 'hear 2'
    settings = config.get_settings()
    config.add_route('home', '/')
    config.add_route('permission', '/permission')
    config.scan(__name__)
