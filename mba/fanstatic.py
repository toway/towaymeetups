from __future__ import absolute_import

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

library = Library("mba", "static")
mba_css = Resource(library, "css/all.css")
resume_edit_js = Resource(library, "js/resume_edit.js")
mba_group = Group([mba_css])
