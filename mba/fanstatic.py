from __future__ import absolute_import

from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

library = Library("mba", "static")
mba_css = Resource(library, "style.css")
mba_form = Resource(library, "js/mbaForm.js")
mba_group = Group([mba_css])
