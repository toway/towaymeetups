#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'


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
from mba import _



class RegisterSchema(colander.Schema):
    name = colander.SchemaNode(
        colander.String(),
        title=_(u'Username'),
    )
    email = colander.SchemaNode(
        colander.String(),
        title=_(u'Email'),
        # TODO:validator
        # validator=deferred_email_validator,
    )



@view_config(route_name='register',renderer='register.jinja2')
def view_register(context, request):
    schema = RegisterSchema().bind(request=request)
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

            appstruct['send_email'] = True
            form = UserAddFormView(context, request)
            form.add_user_success(appstruct)
            success_msg = _(
                '''Congratulations! You are successfully registered.
                You should be receiving an email with a link to set your
                password. Doing so will activate your account.'''
                )
            request.session.flash(success_msg, 'success')
            name = appstruct['name']
            #notify(UserSelfRegistered(get_principals()[name], request))
            return HTTPFound(location=request.application_url)

    if rendered_form is None:
        rendered_form = form.render(request.params)

    api = template_api(
        context, request,
        page_title=_(u"Register - ${title}",
            mapping=dict(title=context.title)),
    )

    return {'api': api, 'form': jinja2.Markup(rendered_form) }


def includeme(config):

    settings = config.get_settings()

    config.add_route('register','/register')
    config.scan(__name__)
