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
from pyramid.encode import urlencode

from kotti import get_settings
from kotti.security import get_principals
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from mba import _

@view_config(route_name='home', renderer='index.jinja2')
def view_home(request):
    return {'project': 'lesson2'}

@view_config(route_name='permission', renderer='index.jinja2', permission='admin')
def view_permission(request):
    return {'project': 'lesson2'}

# TODO groups for mba
def _massage_groups_in(appstruct):
    groups = appstruct.get('groups', [])
    all_groups = list(appstruct.get('roles', [])) + [
        u'group:%s' % g for g in groups if g]
    if 'roles' in appstruct:
        del appstruct['roles']
    appstruct['groups'] = all_groups

class MbaRegisterSchema(RegisterSchema):
    password = colander.SchemaNode(
        colander.String(),
        title=_(u'Password'),
        validator=colander.Length(min=5),
        widget=CheckedPasswordWidget(),
        )

class MbaUserAddFormView(UserAddFormView):
    def add_user_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        _massage_groups_in(appstruct)
        name = appstruct['name'] = appstruct['name'].lower()
        appstruct['email'] = appstruct['email'] and appstruct['email'].lower()
        send_email = appstruct.pop('send_email', False)
        get_principals()[name] = appstruct
        if send_email:
            print 'hear'
            email_set_password(get_principals()[name], self.request)
            self.request.session.flash(
                _(u'${title} was added.',
                  mapping=dict(title=appstruct['title'])), 'success')
            location = self.request.url.split('?')[0] + '?' + urlencode(
                {'extra': name})
            success_msg = _(
                'Congratulations! You are successfully registered. '
                'You should be receiving an email with a link to set your '
                'password. Doing so will activate your account.'
                )
            request.session.flash(success_msg, 'success')
            return HTTPFound(location=location)
        else:
            print 'hear2'
            user = get_principals()[name]
            password = appstruct['password']
            user.password = get_principals().hash_password(password)
            user.confirm_token = None
            headers = remember(self.request, user.name)
            user.last_login_date = datetime.now()
            success_msg = _(
                'Congratulations! You are successfully registered. '
                'You should be receiving an email with a link to set your '
                'password. Doing so will activate your account.'
                )
            self.request.session.flash(success_msg, 'success')
            return HTTPFound(location=self.request.application_url, headers=headers)

#TODO reimplement the kotti.templates.api to use jinja2?
@view_config(route_name='register_old',renderer='register.jinja2')
def view_register(context, request):
    schema = MbaRegisterSchema().bind(request=request)
    form = deform.Form(schema, buttons=('register',))
    rendered_form = None

    if 'register' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()
        else:
            settings = get_settings()

            appstruct['groups'] = u''
            appstruct['roles'] = u''

            register_groups = settings['kotti.register.group']
            if register_groups:
                appstruct['groups'] = [register_groups]

            register_roles = settings['kotti.register.role']
            if register_roles:
                appstruct['roles'] = set(['role:' + register_roles])

            appstruct['send_email'] = False
            form = MbaUserAddFormView(context, request)
            return form.add_user_success(appstruct)

    if rendered_form is None:
        rendered_form = form.render(request.params)

    api = template_api(
        context, request,
        page_title=_(u"Register - ${title}",
            mapping=dict(title=context.title)),
    )

    return {'api': api, 'form': jinja2.Markup(rendered_form)}

def includeme(config):
    #print 'hear 2'
    settings = config.get_settings()
    config.add_route('home', '/')
    config.add_route('permission', '/permission')
    config.add_route('register_old','/register_old')
    config.scan(__name__)
