#!/usr/bin/python
# coding: utf-8

import sys
import datetime
import re
import deform
import colander
import itertools
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.encode import urlencode
from pyramid.response import Response

from kotti import get_settings
from kotti.security import get_principals
from kotti.views.util import template_api
from kotti.views.users import UserAddFormView
from kotti.views.login import RegisterSchema
from mba import _

# http://colander.readthedocs.org/en/latest/basics.html

strip_whitespace = lambda v: v.strip(' \t\n\r') if v is not None else v
remove_multiple_spaces = lambda v: re.sub(' +', ' ', v)

class Friend(colander.TupleSchema):
    rank = colander.SchemaNode(colander.Int(),
                              validator=colander.Range(0, 9999))
    name = colander.SchemaNode(colander.String())

class Phone(colander.MappingSchema):
    location = colander.SchemaNode(colander.String(),
                                  preparer=[strip_whitespace, remove_multiple_spaces],
                                  validator=colander.OneOf(['home', 'work']))
    number = colander.SchemaNode(colander.String())

class Friends(colander.SequenceSchema):
    friend = Friend()

class Phones(colander.SequenceSchema):
    phone = Phone()

class Person(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    age = colander.SchemaNode(colander.Int(),
                             default=20,
                             name='Error age',
                             title='Age',
                             validator=colander.Range(0, 200))
    friends = Friends()
    phones = Phones()

@view_config(route_name='col',renderer='col_test.jinja2')
def view_col(context, request):
    schema = Person().bind(request=request)
    form = deform.Form(schema, buttons=('Test',))
    rendered_form = None
    if 'Test' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()
        else:
            print appstruct
    if rendered_form is None:
        rendered_form = form.render(request.params)
    return {'form': jinja2.Markup(rendered_form)}

@colander.deferred
def deferred_date_validator(node, kw):
    max_date = kw.get('max_date')
    if max_date is None:
        max_date = datetime.date.today()
    return colander.Range(min=datetime.date.min, max=max_date)

@colander.deferred
def deferred_date_description(node, kw):
    max_date = kw.get('max_date')
    if max_date is None:
        max_date = datetime.date.today()
    return 'Blog post date (no earlier than %s)' % max_date.ctime()

@colander.deferred
def deferred_date_missing(node, kw):
    default_date = kw.get('default_date')
    if default_date is None:
        default_date = datetime.date.today()
    return default_date

@colander.deferred
def deferred_body_validator(node, kw):
    max_bodylen = kw.get('max_bodylen')
    if max_bodylen is None:
        max_bodylen = 1 << 18
    return colander.Length(max=max_bodylen)

@colander.deferred
def deferred_body_description(node, kw):
    max_bodylen = kw.get('max_bodylen')
    if max_bodylen is None:
        max_bodylen = 1 << 18
    return 'Blog post body (no longer than %s bytes)' % max_bodylen

@colander.deferred
def deferred_body_widget(node, kw):
    body_type = kw.get('body_type')
    if body_type == 'richtext':
        print 'richtext'
        widget = deform.widget.RichTextWidget(theme='advanced', width=790, height=500)
    else:
        print 'NO richtext'
        widget = deform.widget.TextAreaWidget()
    return widget

@colander.deferred
def deferred_category_validator(node, kw):
    categories = kw.get('categories', [])
    return colander.OneOf([ x[0] for x in categories ])

@colander.deferred
def deferred_category_widget(node, kw):
    categories = kw.get('categories', [])
    return deform.widget.RadioChoiceWidget(values=categories)

class BlogPostSchema(colander.Schema):
    title = colander.SchemaNode(
        colander.String(),
        title = 'Title',
        description = 'Blog post title',
        validator = colander.Length(min=5, max=100),
        widget = deform.widget.TextInputWidget(),
        )
    date = colander.SchemaNode(
        colander.Date(),
        title = 'Date',
        missing = deferred_date_missing,
        description = deferred_date_description,
        validator = deferred_date_validator,
        widget = deform.widget.DateInputWidget(),
        )
    body = colander.SchemaNode(
        colander.String(),
        title = 'Body',
        description = deferred_body_description,
        validator = deferred_body_validator,
        widget = deferred_body_widget,
        )
    category = colander.SchemaNode(
        colander.String(),
        title = 'Category',
        description = 'Blog post category',
        validator = deferred_category_validator,
        widget = deferred_category_widget,
        )

@view_config(route_name='col2',renderer='col_test.jinja2')
def view_col2(context, request):
    schema = BlogPostSchema().bind(
        max_date = datetime.date.max,
        max_bodylen = 5000,
        body_type = 'richtext',
        default_date = datetime.date.today(),
        categories = [('one', 'One'), ('two', 'Two')]
        )
    schema = schema.bind(request=request)

    form = deform.Form(schema, buttons=('Test',))
    rendered_form = None
    if 'Test' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()
        else:
            print appstruct
    if rendered_form is None:
        rendered_form = form.render(request.params)
    return {'form': jinja2.Markup(rendered_form)}

class DocumentSchema(colander.Schema):
    body = colander.SchemaNode(
        colander.String(),
        title=_(u'Body'),
        widget=deform.widget.RichTextWidget(theme='advanced', width=790, height=500),
        missing=u"",
        )

#Not work now and why?
@view_config(route_name='rich',renderer='col_test.jinja2')
def view_rich(context, request):
    schema = DocumentSchema().bind(request=request)
    rendered_form = None
    form = deform.Form(schema, buttons=('Test',))
    rendered_form = form.render(request.params)
    return {'form': jinja2.Markup(rendered_form)}

@view_config(route_name='ajax',renderer='col_ajax.jinja2')
def view_ajax(context, request):
    class Mapping(colander.Schema):
        name = colander.SchemaNode(
                colander.String(),
                description='Content name')
        date = colander.SchemaNode(
                colander.Date(),
                widget=deform.widget.DatePartsWidget(),
                description='Content date')
    class Schema(colander.Schema):
        number = colander.SchemaNode(
                colander.Integer())
        mapping = Mapping()
    schema = Schema()
    def succeed():
        return Response('<div id="thanks">Thanks!</div>')
    submitted = 'submit'
    form = deform.Form(schema, buttons=(submitted,), use_ajax=True)
    if submitted in request.POST:
        try:
            controls = request.POST.items()
            captured = form.validate(controls)
            response = succeed()
            return response
        except deform.ValidationFailure as e:
            print 'hear validation error'
            html = e.render()
            return {'form': jinja2.Markup(html)}
    else:
        rendered_form = form.render(request.params)
        return {'form': jinja2.Markup(rendered_form)}

@view_config(route_name="retail", renderer="mba:templates/retail.pt")
def retail_view(context, request):
    schema = Person().bind(request=request)
    form = deform.Form(schema, buttons=('Test',))
    rendered_form = None
    if 'Test' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())
        except ValidationFailure, e:
            request.session.flash(_(u"There was an error."), 'error')
            rendered_form = e.render()
        else:
            print appstruct
    return {
            'field':form,
            }

class FormCustom(deform.Form):
    def __init__(self, schema, **kw):
        super(FormCustom, self).__init__(schema, **kw)
        template = kw.pop('template', None)
        #TODO for readonly_template
        if template:
            self.widget = deform.widget.FormWidget(template=template)


@view_config(route_name='formtest', renderer='col_test.jinja2')
def formtest_view(context, request):

    options = """
    {success:
        function (rText, sText, xhr, form) {
            var loc = xhr.getResponseHeader('X-Relocate');
            if (loc) {
                document.location = loc;
            }
        }
    }
    """

    counter = itertools.count()
    class Schema1(colander.Schema):
        name1=colander.SchemaNode(colander.String())
    schema1 = Schema1()
    form1 = FormCustom(schema1, template='form1', use_ajax=True, ajax_options=options
            , buttons=('submit',),formid="form1", counter=counter)
    
    class Schema2(colander.Schema):
        name2 = colander.SchemaNode(colander.String())
    schema2 = Schema2()
    form2 = FormCustom(schema2, template='form1', use_ajax=True, ajax_options=options
            , buttons=('submit',), formid="form2", counter=counter)
    html = []
    captured = None
    if 'submit' in request.POST:
        posted_formid = request.POST['__formid__']
        for (formid,form) in [('form1', form1), ('form2', form2)]:
            if formid == posted_formid:
                try:
                    controls = request.POST.items()
                    captured = form.validate(controls)
                    #html.append(form.render(captured))
                    #return Response('<div id="thanks">Thanks!</div>')
                    return Response(
                            '<div>hurr</div>',
                            headers=[('X-Relocate', '/'), ('Content-Type','text/html')]
                            )
                except deform.ValidationFailure as e:
                    html.append(e.render())
            else:
                html.append(form.render())
    else:
        for form in form1,form2:
            html.append(form.render())
    html = u''.join(html)
    return {
            'captured':repr(captured),
            'form': jinja2.Markup(html)
            }


def includeme(config):
    settings = config.get_settings()
    config.add_route('col','/col')
    config.add_route('col2','/col2')
    config.add_route('rich','/rich')
    config.add_route('ajax','/ajax')
    config.add_route('retail','/retail')
    config.add_route('formtest','/formtest')
    config.scan(__name__)
