__author__ = 'sunset'

from deform.widget import Widget, TextInputWidget


class URLInputWidget(TextInputWidget):
    def serialize(self, field, cstruct, **kw):
        urlinput = TextInputWidget.serialize(self, field, cstruct, **kw)
        return "http://xxx/" + urlinput

