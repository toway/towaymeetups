#!/usr/bin/python
# coding: utf-8


__author__ = 'sunset'

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, TextInputWidget
from deform.widget import RichTextWidget
from deform.widget import TextAreaWidget

from js.jquery import jquery

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from pyramid.decorator import reify

from kotti.views.form import AddFormView, EditFormView
from kotti.interfaces import IContent
from kotti import DBSession
from kotti.security import get_user

from mba.resources import get_act_root, get_review_root, get_info_root
from mba.resources import MbaUser, Act, Review, Comment, Infomation
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.fanstatic import city_css
from mba.views.widget import URLInputWidget
from mba.views.view import MbaTemplateAPI
from mba import _

__author__ = 'sunset'
__date__ = '20140904'


    
class InfoSchema(colander.MappingSchema):
    title = colander.SchemaNode(    
            colander.String(), 
            title=u'标题')

    body = colander.SchemaNode(
            colander.String(),
            title = u'内容',
            widget=RichTextWidget(theme='modern'
                , template = 'richtext.jinja2'
                , width=790
                , height=500),
        )
        
class InfoAddForm(AddFormView):
    schema_factory = InfoSchema
    add = Infomation
        
    item_type = _(u"推荐信息")
    form_options = ({'css_class':'form-horizontal'}) 


    def __call__(self):
        ret = AddFormView.__call__(self)
        if isinstance(ret, dict):            
            ret = wrap_user2(self.request, ret)
            ret.update({'api': MbaTemplateAPI(self.context, self.request)})            
        return ret

    
    
    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = self.find_name(appstruct)        
        parent = get_info_root()
        new_item = parent[name] = self.add(default_view='info_view', **appstruct)
        self.request.session.flash(self.success_message, 'success')
        location = self.success_url or self.request.resource_url(new_item)
        return HTTPFound(location=location) 

class InfoEditForm(EditFormView):
    schema_factory = InfoSchema
    
    def __init__(self, context, request, **kwargs):
        
        id = request.matchdict['id']
        info = DBSession.query(Infomation).filter_by(id=id).one()
        context = info
        
        EditFormView.__init__(self, context, request, **kwargs)
        
@view_config(name='info_view', context=IContent, renderer='infomation.jinja2')
def view_review(context, request):  
    jquery.need()    
    contextbody = jinja2.Markup(context.body)

    user = get_user(request)

    if request.POST :

        if user is None:
            request.session.flash(u"请先登陆..","info")
            came_from = request.url
            return HTTPFound("/login?came_from=%s" % came_from)

        if 'submit' in request.POST:


            comment_content = request.params.get("infomation-comment-input")

            comment = Comment()
            comment.type = comment.TYPE_INFOMATION
            comment.user_id = user.id
            comment.document_id = context.id

            # ACTION!!!: There is a SQL injection risk here! should be prevented
            comment.content =  comment_content
            DBSession.add( comment)
            DBSession.flush()

    return  wrap_user2(request, 
                {'context':context, 
                'contextbody': contextbody,
                })       

def includeme(config):    
    config.scan(__name__)                