__author__ = 'sunset'
__date__ = '20140813'

import json

from kotti.resources import Content
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import view_defaults

from kotti_tinymce import KottiTinyMCE



@view_defaults(context=Content,
               request_method="GET")
class MBAOverrideKottiMCE(KottiTinyMCE):
    """ There are some bugs exist in the KottiTinyMCE(version=0.4.2) that do not match
        the js.tinymce(version=4.0.2), so we do some modifications here to balance them
    """

    @view_config(name="external_link_list2")
    def external_link_list(self):
        links = []
        for n in self.context.children:
            url = self.request.resource_url(n)
            path = url.replace(self.request.application_url, "")
            links.append([u"%s (%s)" % (path, n.title),
                          url])
        links.sort(key=lambda x: x[0])
        response = " %s" % json.dumps(links)

        return Response(body=response)

    @view_config(name="external_image_list2")
    def external_image_list(self):

        images = []
        for n in self.context.children:
            if n.type != 'image':
                continue
            url = self.request.resource_url(n)
            path = url.replace(self.request.application_url, "")
            # images.append([u"%s (%s)" % (path, n.title),
            #                "%simage" % url])
            images.append({'title': n.title,
                           'url': url,
                           'value': url+ 'image' ,
                           'path': path,
                           #'menu': 3
            })
        # images.sort(key=lambda x: x[0])

        # response = "var tinyMCEImageList = %s;" % json.dumps(images)
        response = " %s" % json.dumps(images)

        return Response(body=response)


def includeme(config):
    config.scan(__name__)