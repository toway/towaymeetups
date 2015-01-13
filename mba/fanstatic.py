from __future__ import absolute_import

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

from js.jquery import jquery

library = Library("mba", "static")
mba_css = Resource(library, "css/all.css")
mba_js =  Resource(library, "js/main.js")
mba_global = Group([mba_css, mba_js])

bootstrap_css = Resource(library, 'bootstrap-3.2.0/css/bootstrap.css')
bootstrap_js = Resource(library, 'bootstrap-3.2.0/js/bootstrap.js', depends=[jquery])
bootstrap = Group([bootstrap_css, bootstrap_js])


mba_widget_css = Resource(library, 'css/mba_widgets.css')
mba_widget_js = Resource(library, 'js/mba_widgets.js' ,depends=[jquery, mba_widget_css])
mba_widget = Group([mba_widget_css, mba_widget_js])




resume_edit_js = Resource(library, "js/resume_edit.js")
city_css = Resource(library, "css/city.css")


