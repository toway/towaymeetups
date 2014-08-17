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

from mba.resources import get_act_root, get_review_root
from mba.resources import MbaUser, Act, Review, Comment
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.fanstatic import city_css
from mba.views.widget import URLInputWidget
from mba.views.view import MbaTemplateAPI
from mba import _

__author__ = 'sunset'
__date__ = '20140725'

@colander.deferred
def deferred_meetups_widget(node, kw):
    widget = deform.widget.SelectWidget(values=[ (str(i.id), i.title) 
                                                   for i in DBSession.query(Act).all() ],
                                          css_class='form-control')
    return widget    
    
class ReviewSchema(colander.MappingSchema):
    title = colander.SchemaNode(    
            colander.String(), 
            title=u'标题')
    
    review_to_meetup_id = colander.SchemaNode(
            colander.String(),
            title = u'相应活动',
            widget=deferred_meetups_widget)
            
    body = colander.SchemaNode(
            colander.String(),
            title = u'内容',
            widget=RichTextWidget(theme='modern'
                , template = 'richtext.jinja2'
                , width=790
                , height=500),
        )
        
class ReviewAddForm(AddFormView):
    schema_factory = ReviewSchema
    add = Review
        
    item_type = _(u"活动回顾")
    form_options = ({'css_class':'form-horizontal'}) 
    
    
        
    def __init__(self, context, request, **kw):
        
       
        self.meetup_id =   request.params.get('meetup-id', "0") 
        AddFormView.__init__(self, context, request, **kw)
        
    def before(self, form):
        form.appstruct = {'review_to_meetup_id': self.meetup_id }        
    
    def __call__(self):
        ret = AddFormView.__call__(self)
        if isinstance(ret, dict):            
            ret = wrap_user2(self.request, ret)
            ret.update({'api': MbaTemplateAPI(self.context, self.request)})            
        return ret
        
    # def appstruct(self):
        # appst = AddFormView.appstruct(self)
        # print (appst)

        # if appst is None:
            # appst = {'review_to_meetup': self.meetup_id }
        # else:
            # appst.update( {'review_to_meetup': self.meetup_id } )
            
        # return appst
    
    # add_template_vars  = ('review_to_meetup',)
    # @reify
    # def review_to_meetup(self):
        # return self.meetup_id
    
    
    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        name = self.find_name(appstruct)        
        parent = get_review_root()
        new_item = parent[name] = self.add(default_view='review_view', **appstruct)
        self.request.session.flash(self.success_message, 'success')
        location = self.success_url or self.request.resource_url(new_item)
        return HTTPFound(location=location) 

class ReviewEditForm(EditFormView):
    schema_factory = ReviewSchema
    
    def __init__(self, context, request, **kwargs):
        
        id = request.matchdict['id']
        meetup = DBSession.query(Review).filter_by(id=id).one()
        context = meetup
        
        EditFormView.__init__(self, context, request, **kwargs)
        
@view_config(name='review_view', context=IContent, renderer='review.jinja2')
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

            
            comment_content = request.params.get("review-comment-input")
            
            comment = Comment()
            comment.type = comment.TYPE_MEETUP_REVIEW
            comment.user_id = user.id
            comment.document_id = context.id 
            
            # ACTION!!!: There is a SQL injection risk here! should be prevented
            comment.content =  comment_content
            DBSession.add( comment)
            DBSession.flush()
            

        
    return  wrap_user2(request, 
                {'context':context, 
                'contextbody': contextbody,
                'comments_count': len(context.comments)                
                })       

def includeme(config):    
    config.scan(__name__)                