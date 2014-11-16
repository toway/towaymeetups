__author__ = 'sunset'

import StringIO

from pyramid.view import view_config
from pyramid.request import Request,Response
from kotti import DBSession

from mba.utils.captcha import create_validate_code

@view_config(route_name='captcha')
def captcha(request):
    import os
    print os.getcwd()
    img, code = create_validate_code(
        font_type="mba/static/fonts/open-sans/OpenSans-Regular.ttf",
        size=(60,30))
    buf = StringIO.StringIO()
    img.save(buf, 'JPEG', quality=70)
    bufval = buf.getvalue()

    return Response(content_type='image/jpeg', body=bufval)


def includeme(config):
    config.add_route('captcha','/captcha.jpg')
    config.scan(__name__)