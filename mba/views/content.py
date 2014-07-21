import random
from StringIO import StringIO
import colander
from colander import SchemaNode
from colander import null
from deform import FileData
from deform.widget import FileUploadWidget
from deform.widget import RichTextWidget
from deform.widget import TextAreaWidget

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

class MbaImageAddForm(ImageAddForm):
    def __init__(self, context, request, **kwargs):
        super(FileAddForm, self).__init__(None, request)
        self.context = get_image_root()

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
