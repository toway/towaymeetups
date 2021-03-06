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
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.views.view import MbaTemplateAPI
from mba.utils.validators import name_pattern_validator

@view_config(route_name='home2', renderer='index2.jinja2')
def view_home(request):
    #only for test
    #stu = DBSession.query(MbaUser).filter_by(email='a@gmail.com').first()
    #headers = remember(request, stu.name)
    #response = render_to_response('index2.jinja2', {'project':'lession2'}, request=request)
    #response.headerlist.extend(headers)
    #return response
    return {}

@view_config(route_name='permission', renderer='index.jinja2', permission='admin')
def view_permission(request):
    return {'project': 'lesson2'}
    


def login_pattern_validator(node, value):
    try:
        colander.Email()(node, value)
    except colander.Invalid, ex:
        try:
            name_pattern_validator(node, value)
        except colander.Invalid, ex:
            raise colander.Invalid(node, _(u"不合法的用户名或Email格式"))


class LoginSchema(colander.Schema):
    email_or_username = colander.SchemaNode(
        colander.String(),
        title=_(u'邮箱、用户名或手机号'),
        validator=login_pattern_validator
    )
    password = colander.SchemaNode(
        colander.String(),
        title=_(u'密码 <a href="/iforgot">(忘记了?)</a>'),
        validator=colander.Length(min=6),
        widget=deform.widget.PasswordWidget(css_class='form-control'),
        )
import re
phone_reg = re.compile('^\d{11}$')
def _find_user(login):

    print login
    principals = get_principals()

    if phone_reg.match(login):
        print 'match'
        for p in principals.search(phone=login):
            return p

    else:




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

def user_password_match_validator(form, value):
    """ TODO: Doesn't take effect yet
    """
    principals = get_principals()
    principal = principals.get(value['email_or_username'])



@view_config(name='login', renderer='login.jinja2')
def login(context, request):

    user = get_user(request)
    if user :
        # already login, redirect to home page
        return HTTPFound(location="/")
    
    schema = LoginSchema(validator=user_password_match_validator).bind(request=request)

    form = deform.Form(schema,
                       buttons=[deform.form.Button(u'submit', title=u'登录', css_class="btn btn-primary")],
                       css_class="border-radius: 4px;box-shadow: 0 1px 3px rgba(0,0,0,0.075);" )
    rendered_form = None

    principals = get_principals()

    came_from = request.params.get(
        'came_from', request.resource_url(context))
    login, password = u'', u''

    if 'submit' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            # msg = [ _(u"%s is %s")  for (k,v) in  e.error.items() ]    
            # msg = u",".join( [m for m in e.error.messages] )
            request.session.flash(_(u"登陆失败" ), 'danger')
            #request.session.flash(_(u"登陆失败：%s" % e.error), 'error')
            # showing 登陆失败 {'password': u'shorting than miminum length 6'}
            rendered_form = e.render()
        else:
            user = _find_user(appstruct['email_or_username'])
            if (user is not None and user.status == user.ACTIVE and
                    principals.validate_password(appstruct['password'], user.password)):
                headers = remember(request, user.name)

                # TODO: i18n does not work
                # request.session.flash(
                #     _(u"欢迎登陆, ${user}!",
                #       mapping={'user': 'sb' }), 'success')
                # request.session.flash(
                #     _(u"欢迎登陆, %s!" % (user.real_name or user.name ) ), 'success')
                user.last_login_date = datetime.now()
                if came_from == 'login':
                    came_from = '/'
                return HTTPFound(location=came_from, headers=headers)

            elif user.status == user.INACTIVE:
                return HTTPFound(location='/register_finish')
            elif user.status == user.TO_FULLFIL_DATA:
                headers = remember(request, user.name)
                return HTTPFound(location='/register_details', headers=headers)

            request.session.flash(_(u"登陆失败，用户名或密码错误."), 'danger')

    if rendered_form is None:
        rendered_form = form.render(request.params)

    return  {'form': jinja2.Markup(rendered_form)}


@view_config(route_name="prelogin", renderer='prelogin.jinja2')
def view_prelogin(context, request):
    return {'aaa':'bbb'}

@view_config(name='forbidden', renderer='col_test.jinja2')
@wrap_user
def forbidden_view_html(request):
    return {'form':'Forbidden'}

def includeme(config):
    #print 'hear 2'
    settings = config.get_settings()
    config.add_route('home2', '/index_2')
    config.add_route('prelogin','/prelogin')
    config.add_route('permission', '/permission')

    config.scan(__name__)
