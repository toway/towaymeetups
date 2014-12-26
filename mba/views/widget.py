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

class ImageUploadWidget2(ImageUploadWidget):
    template = "imageupload2"


class GeoWidget(MappingWidget):
    template = "qqmap_input"
    def handle_error(self, field, error):
        """
        The ``handle_error`` method of a widget must:

        - Set the ``error`` attribute of the ``field`` object it is
          passed, if the ``error`` attribute has not already been set.

        - Call the ``handle_error`` method of each subfield which also
          has an error (as per the ``error`` argument's ``children``
          attribute).
        """

        # Get the only error children to show is OK!

        if field.error is None:
            field.error = error
        for e in error.children:
            for num, subfield in enumerate(field.children):
                if e.pos == num:
                    # subfield.widget.handle_error(subfield, e)
                    field.error = e
                    break


class PhoneValidateCodeInputWidget(TextInputWidget):
    template = "phonevalidatecode_input"
