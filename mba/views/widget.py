__author__ = 'sunset'

from colander import null

from deform.widget import Widget, TextInputWidget, MappingWidget
from colander import Invalid



class URLInputWidget(TextInputWidget):
    template = "urlinput"


class ImageUploadWidget(Widget):
    template = "imageupload"

    strip = True


    requirements = ( ('jquery', None), )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)

    def deserialize(self, field, pstruct):
        if pstruct is null:
            return null
        if self.strip:
            pstruct = pstruct.strip()
        if not pstruct:
            return null
        return pstruct

class GeoWidget(MappingWidget):
    template = "qqmap_input"

