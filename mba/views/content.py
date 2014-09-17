#!/usr/bin/python
# coding: utf-8


import datetime
from random import randint

try:
    import json
except  ImportError:
    import simplejson as json


from StringIO import StringIO
import colander
from colander import SchemaNode
from colander import null

from pyramid.view import view_config
from pyramid.view import view_defaults

import deform
from deform import FileData
from deform.widget import FileUploadWidget, HiddenWidget
from deform.widget import RichTextWidget
from deform.widget import TextAreaWidget,TextInputWidget

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response


from kotti.resources import Document
from kotti.resources import File
from kotti.resources import Image
from kotti.util import _
from kotti.views.form import get_appstruct
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from kotti.views.form import FileUploadTempStore
from kotti.views.form import ObjectType
from kotti.views.form import deferred_tag_it_widget
from kotti.views.form import validate_file_size_limit

from kotti.views.edit.content import *

from mba.resources import get_image_root
from mba.utils import RetDict



def validate_image_type(node, value):
    """
    """
    filetype = value['mimetype']
    if not filetype.startswith("image/"):
        raise colander.Invalid(node, u"非法的图片类型")

def ImageSchema(tmpstore, title_missing=None):
    class ImageSchema(colander.MappingSchema):
        title = SchemaNode(
            colander.String(),
            title=u"",
            widget=HiddenWidget())

        file = SchemaNode(
            FileData(),
            title=u'',
            missing=u"",
            widget=FileUploadWidget(tmpstore),
            validator=colander.All(
                validate_file_size_limit,
                validate_image_type
            ))

    def set_title_missing(node, kw):
        if title_missing is not None:
            node['title'].missing = title_missing
    return ImageSchema(after_bind=set_title_missing)


class MbaImageAddForm(ImageAddForm):



    form_options = {'action': '/add_image_iframe'}

    def schema_factory(self):
        tmpstore = FileUploadTempStore(self.request)
        return ImageSchema(tmpstore, title_missing=null)

    def __init__(self, context, request, **kwargs):
        super(ImageAddForm, self).__init__(None, request)
        self.context = get_image_root()

    def add(self, **appstruct):
        appstruct['title'] = None
        appstruct['description'] = ''
        appstruct['tags'] = []

        item_class = ImageAddForm.add(self, **appstruct)
        item_class.default_view ="image_view"
        return item_class

    def random_filename(self):
        now = datetime.datetime.now()
        nowt = now.strftime('%Y%m%d%H%M%S')
        postfix = ""

        for i in range(10):
            r = randint(0,2)
            o = (
                randint(ord('A'),ord('Z') ) ,
                randint(ord('a'),ord('z') ),
                randint(ord('0'),ord('9') )
            )
            postfix += chr(o[r])

        return "%s_%s" % (nowt, postfix)

    def save_success(self, appstruct):
        appstruct['name'] = self.random_filename()
        return super(ImageAddForm, self).save_success(appstruct)

class MbaImageAddForm2(MbaImageAddForm):
    buttons = (
        deform.Button('save',u"上传"),
        deform.Button('cancel', u"取消"))


    def failure(self, e):
        ret = MbaImageAddForm.failure(self, e)
        ret['upload_success'] =  False
        return ret


    def save_success(self, appstruct):

        appstruct.pop('csrf_token', None)
        name = appstruct['name'] = self.random_filename()

        # name = self.find_name(appstruct)
        new_item = self.context[name] = self.add(**appstruct)


        img_url =  self.request.resource_url(new_item) + "image"


        return {"upload_success": True, "img_url": img_url }

        # self.request.session.flash(self.success_message, 'success')


        # ret = RetDict(retval=location+"image")

        # return Response(content_type="text/plain",body=json.dumps(ret))









    @view_config( name="image_upload_view")
    def upload(self):
        return Response("OK")

def includeme(config):
    config.add_view(
        FileEditForm,
        context=File,
        name='edit',
        renderer='col_test.jinja2',
        )

    config.add_view(
        FileAddForm,
        name=File.type_info.add_view,
        renderer='col_test.jinja2',
        )

    config.add_view(
        ImageEditForm,
        context=Image,
        name='edit',
        renderer='col_test.jinja2',
        )

    config.add_view(
        MbaImageAddForm,
        name=Image.type_info.add_view,
        renderer='col_test.jinja2',
        )

    config.add_view(
        MbaImageAddForm2,
        name="add_image_iframe",
        renderer='image_upload_iframe.jinja2',
        )