#!/usr/bin/python
# coding: utf-8


"""
Views for image content objects.
"""

import PIL
from plone.scale.scale import scaleImage
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import view_defaults

from js.jquery import jquery

from kotti.interfaces import IImage
from kotti.util import extract_from_settings
from kotti.security import get_user

PIL.ImageFile.MAXBLOCK = 33554432

#: Default image scales
image_scales = {
    'span1': [60, 120],
    'span2': [160, 320],
    'span3': [260, 520],
    'span4': [360, 720],
    'span5': [460, 920],
    'span6': [560, 1120],
    'span7': [660, 1320],
    'span8': [760, 1520],
    'span9': [860, 1720],
    'span10': [960, 1920],
    'span11': [1060, 2120],
    'span12': [1160, 2320],
    }


@view_defaults(context=IImage)
class ImageView(object):
    """The ImageView class is registered for the :class:`IImage` context."""

    def __init__(self, context, request):

        print "ImageView __init__"

        self.context = context
        self.request = request


    @view_config(name='image_view',
                 renderer='image_view.jinja2')
    def view(self):
        """
        :result: Empty dictionary to be handed to the image.pt template for rendering.
        :rtype: dict
        """

        jquery.need()

        return {'image_id': self.context.id}

    @view_config(name="image",)
    def image(self, subpath=None):
        """Return the image in a specific scale, either inline
        (default) or as attachment.

        :param subpath: [<image_scale>]/download] (optional).
                        When 'download' is the last element in subpath,
                        the image is served with a 'Content-Disposition: attachment'
                        header.  <image_scale> has to be one of the predefined
                        image_scales - either from the defaults in this module
                        or one set with a kotti.image_scales.<scale_name> in your
                        app config ini file.
        :type subpath: str

        :result: complete response object
        :rtype: pyramid.response.Response
        """


        if subpath is None:
            subpath = self.request.subpath

        width, height = (None, None)
        subpath = list(subpath)

        if (len(subpath) > 0) and (subpath[-1] == "download"):
            disposition = "attachment"
            subpath.pop()
        else:
            disposition = "inline"

        if len(subpath) == 1:
            scale = subpath[0]
            if scale in image_scales:
                # /path/to/image/scale/thumb
                width, height = image_scales[scale]

        if width and height:
            image, format, size = scaleImage(self.context.data,
                                             width=width,
                                             height=height,
                                             direction="thumb")
        else:
            image = self.context.data

        res = Response(
            headerlist=[('Content-Disposition', '%s;filename="%s"' % (
                disposition,
                self.context.filename.encode('ascii', 'ignore'))),
                ('Content-Length', str(len(image))),
                ('Content-Type', str(self.context.mimetype)),
            ],
            body=image,
            )

        return res


def _load_image_scales(settings):
    image_scale_strings = extract_from_settings(
        'kotti.image_scales.', settings)

    for k in image_scale_strings.keys():
        image_scales[k] = [int(x) for x in image_scale_strings[k].split("x")]

from cStringIO import StringIO
from PIL import Image
from datetime import datetime

@view_config(route_name="avatarUpload", renderer='json')
def avatar_upload(context, request):

    user = get_user(request)
    if not user:
        return {"code":401, "msg": u"请先登陆", "pid": 0}


    # print(img)
    # img.save("abc.png")
    # img.save("abc.jpg")
    # img.save("abc80.jpg", quality=80)

    try:

        # learn from :http://stackoverflow.com/questions/19816033/converting-binary-file-into-pil-image-datatype-in-google-app-engine
        imgfile = StringIO(request.body)
        img = Image.open(imgfile)

        now = datetime.now()
        img_name = "avatar%d_%s.jpg" % ( user.id, now.strftime("%Y%m%d%H%M%S") )
        img.save('mba/static/img/avatars/%s' % img_name, quality=85)

        user.avatar = '/fanstatic/mba/img/avatars/%s' % img_name

        return {"code":200, "msg": user.avatar, "pid": 0}

    except Exception, ex:

        errmsg = "%s" % ex
        return {"code":500, "msg": errmsg, "pid": 0}




def includeme(config):
    _load_image_scales(config.registry.settings)

    config.add_route('avatarUpload', "/avatarUpload")

    config.scan(__name__)
