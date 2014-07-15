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
from pyramid.renderers import render
from deform.widget import RichTextWidget

from kotti import get_settings
from kotti.views.form import AddFormView
from kotti.views.edit.content import ContentSchema
from kotti.resources import Document
from kotti.interfaces import IContent
#from kotti.util import TemplateStructure
from mba import _

class FormCustom(deform.Form):
    def __init__(self, schema, **kw):
        #super(FormCustom, self).__init__(schema, **kw)
        deform.Form.__init__(self, schema, **kw)


        template = kw.pop('template', None)
        if template:
            self.widget.template = template
        readonly_template = kw.pop('readonly_template', None)
        if readonly_template:
            self.widget.readonly_template = readonly_template
        
        self.child_dict = {}
        for field in self.children:
            self.child_dict[field.name] = field

    def custom_render(self, name):
        f = self.child_dict[name]
        cstruct = self.cstruct
        return self.renderer(self.widget.item_template, field=f
                , cstruct=cstruct.get(f.name, colander.null))

class DocumentSchema(ContentSchema):
    body = colander.SchemaNode(
        colander.String(),
        title=_(u'Body'),
        widget=RichTextWidget(theme='modern'
            , template = 'richtext.jinja2'
            , width=790
            , height=500),
        )

class DocumentAddForm(AddFormView):
    schema_factory = DocumentSchema
    add = Document
    item_type = _(u"Document")

class TemplateStructure(object):
    def __init__(self, html):
        self.html = html

    def __html__(self):
        return self.html
    __unicode__ = __html__

    def __getattr__(self, key):
        return getattr(self.html, key)

class MbaTemplateAPI(object):
    def __init__(self, context, request, bare=None, **kwargs):
        self.context, self.request = context, request

        if getattr(request, 'template_api', None) is None:
            request.template_api = self

    def render_template(self, renderer, **kwargs):
        return TemplateStructure(render(renderer, kwargs, self.request))

from mba.utils import wrap_user
from js.jquery import jquery
@view_config(name='test_view', context=IContent, renderer='meetup.jinja2')
def test_view(context, request):
    api = MbaTemplateAPI(context, request)
    jquery.need()
    return wrap_user(request,{'api': api, 'context':context})

def includeme(config):
    config.add_view(
        DocumentAddForm,
        name=Document.type_info.add_view,
        #permission='add',
        renderer='col_test.jinja2',
        )
    config.scan(__name__)
