from __future__ import absolute_import

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

from js.jquery import jquery

library = Library("mba", "static")
mba_css = Resource(library, "css/all.css")
mba_js =  Resource(library, "js/main.js")

bootstrap_css = Resource(library, 'bootstrap-3.2.0/css/bootstrap.css')
bootstrap_js = Resource(library, 'bootstrap-3.2.0/js/bootstrap.js', depends=[jquery])
bootstrap = Group([bootstrap_css, bootstrap_js])



mba_group = Group([mba_css, mba_js])


resume_edit_js = Resource(library, "js/resume_edit.js")
city_css = Resource(library, "css/city.css")


