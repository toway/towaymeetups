#!/usr/bin/python
# coding: utf-8

import deform
import colander
import jinja2
from pyramid.view import view_config

@view_config(route_name='home', renderer='index.jinja2')
def view_home(request):
    return {'project': 'lesson2'}


@view_config(route_name='register',renderer='register.jinja2')
def view_register(request):
    class Schema(colander.Schema):
        name = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(max=100),
            title=u"name",
             input_append="kg",
            widget=deform.widget.TextInputWidget(size=60))

        classno = colander.SchemaNode(
            colander.String(),
            title=u"classnumber",
            input_append="kg",

        )




    schema = Schema()
    form = deform.Form(schema, buttons=('submit',))
    html = form.render()


    return {'form': jinja2.Markup(html) }


    # return self.render_form(form)