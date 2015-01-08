__author__ = 'sunset'

import json
import datetime
from colander import null

from deform.widget import Widget, TextInputWidget, MappingWidget, DateTimeInputWidget, DateInputWidget
from colander import Invalid

from colander import iso8601

from mba import  _



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


from colander import DateTime

class DateTimeRange(DateTime):


    def serialize(self, node, appstructtuple):
        # print 'colander datetimerange serialize', appstructtuple, node

        # print 'DateTimeRange serialize:', appstructtuple

        if not appstructtuple:
            return null

        ret = []
        for appstruct in appstructtuple:

            if type(appstruct) is datetime.date: # cant use isinstance; dt subs date
                appstruct = datetime.datetime.combine(appstruct, datetime.time())

            if not isinstance(appstruct, datetime.datetime):
                raise Invalid(node,
                              _('"${val}" is not a datetime object',
                                mapping={'val':appstruct})
                              )

            if appstruct.tzinfo is None:
                appstruct = appstruct.replace(tzinfo=self.default_tzinfo)

            ret.append( appstruct.isoformat() )

        return ret

    def deserialize(self, node, cstructdict):
        if not cstructdict:
            return null

        # print 'DateTimeRange deserialize:', cstructdict

        ret = []


        # for (key,cstruct) in cstructdict.items():
        for cstruct in cstructdict:


            try:
                result = iso8601.parse_date(
                    cstruct, default_timezone=self.default_tzinfo)
            except (iso8601.ParseError, TypeError) as e:
                try:
                    year, month, day = map(int, cstruct.split('-', 2))
                    result = datetime.datetime(year, month, day,
                                               tzinfo=self.default_tzinfo)
                except Exception as e:
                    raise Invalid(node, _(self.err_template,
                                          mapping={'val':cstruct, 'err':e}))

            # ret[key] = result
            ret.append(result)

        return ret

class DateTimeRangeInputWidget(DateTimeInputWidget):
    template = "datetimerange"
    default_options = (DateInputWidget.default_options +
                       (('timeFormat', 'HH:mm:ss'),
                        ('separator', ' ')))


    def deserialize(self, field, pstruct):
        # print 'DateTimeRangeInputWidget deserialize:', pstruct
        if pstruct in ('', null):
            return null



        ret = []
        for index, item in enumerate(pstruct):
            if item in ('', null):
                return null

            timeitem = item.replace(self.options['separator'], 'T')
            ret.append(timeitem)
            # ret[self.control_names[index]] = timeitem
            # ret[self.control_names[timeitem])

        return ret

    def serialize(self, field, cstruct, **kw):

        # print 'DateTimeRangeInputWidget serialize:', cstruct

        if cstruct in (null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)

        kw['control_names'] = self.__dict__.get('control_names')



        options = kw.get('options', self.options)
        kw['options'] = json.dumps(options)
        separator = options.get('separator', ' ')

        constructed = []
        for comp in cstruct:
            # if type(comp) is datetime.date: # cant use isinstance; dt subs date
            #     comp = datetime.datetime.combine(comp, datetime.time())
            #
            # comp = comp.isoformat()

            if len(comp) == 25: # strip timezone if it's there
                comp = comp[:-6]

            comp = separator.join(comp.split('T'))

            constructed.append(comp)
        values = self.get_template_values(field, constructed, kw)
        # print 'values:', values
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **values)