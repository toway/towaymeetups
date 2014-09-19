#!/usr/bin/python
# coding: utf-8

from datetime import datetime

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget, HiddenWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email
from pyramid.request import Response

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user
from kotti.views.form import AddFormView, EditFormView


from mba import _
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.views.infomation import InfoAddForm, InfoEditForm
from mba.resources import Banner
from mba.views.widget import ImageUploadWidget2

from js import fineuploader
from js.jquery import jquery


from mba.utils import RetDict

__author__ = 'sunset'
__date__ = '20140916'
__desc__ = u'首页BANNER管理'







class BannerSchema(colander.MappingSchema):


    title = colander.SchemaNode(
        colander.String(),
        title=_(u'BANNER标题'),

        )


    img_url = colander.SchemaNode(
        colander.String(),
        title=_(u'BANNER'),
        description=_(u'上传BANNER'),
        #widget=ImageUploadWidget(title=_(u"上传BANNER"))
        widget=ImageUploadWidget2()
    )


    link_url = colander.SchemaNode(
        colander.String(),
        title=_(u'链接到的地址'),
        description=_(u'点击链接到的地址'),
        #widget=ImageUploadWidget(title=_(u"上传BANNER"))
    )



@view_config(route_name='admin_home_banner_add', renderer='admin/banner_add.jinja2',permission='view')
class BannerAddForm(AddFormView):
    schema_factory = BannerSchema
    add = Banner

    item_type = _(u"BANNER")

    form_options = ({'css_class':'form-horizontal'})

    success_url = "/admin/banners"

    def __call__(self):
        ret = AddFormView.__call__(self)
        if isinstance(ret, dict):
            ret = wrap_user2(self.request, ret)
        return ret


    def save_success(self, appstruct):
        appstruct.pop('csrf_token', None)
        DBSession.add( self.add(**appstruct) )

        self.request.session.flash(self.success_message, 'success')
        location = self.success_url
        return HTTPFound(location=location)

@view_config(route_name='admin_home_banner_edit', renderer='admin/banner_add.jinja2',permission='view')
class BannerEditForm(EditFormView):

    buttons = (
        deform.Button('update', _(u'更新')),
        deform.Button('cancel', _(u'取消')))

    schema_factory = BannerSchema

    success_url = "/admin/banners"


    def __init__(self, context, request, **kwargs):

        id = request.matchdict['id']
        banner = DBSession.query(Banner).filter_by(id=id).one()
        context = banner

        EditFormView.__init__(self, context, request, **kwargs)


    def __call__(self):
        ret = EditFormView.__call__(self)
        if isinstance(ret, dict):
            ret = wrap_user2(self.request, ret)
        return ret

    def update_success(self, appstruct):
        return self.save_success(appstruct)




@view_config(route_name='admin_home_banners', renderer='admin/banners.jinja2',permission='view')
@view_config(route_name='admin_home_banners', renderer='json',permission='view',xhr=True)
def admin_home_banners(context, request):
    jquery.need()

    user = get_user(request)
    if not user:
        return HTTPFound(location="/login?came_from=%s" % request.url)




    if 'method' in request.POST:
        # mt stands for meetup-type
        try:
            method = request.POST['method'] # del-banner

            if method  == 'del-banner':



                mt_id = int(request.POST['banner-id'])

                to_op_mt = DBSession.query(Banner).filter_by(id=mt_id).first()



                banner_id = request.POST.get('banner-id', None)

                if not banner_id :
                    return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)

                try:
                    banner_id = int(banner_id)
                except ValueError,e:
                    return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


                banner = DBSession.query(Banner).filter_by(id=banner_id).first()

                if not banner:
                    return RetDict(errcode=RetDict.ERR_CODE_WRONG_PARAM)


                DBSession.delete(banner)

                msg = u"成功删除BANNER %d" % banner_id

                request.session.flash(msg, 'success')

                return RetDict(retval=msg)




        except Exception,ex:
            err_msg = "错误：%s" % ex
            request.session.flash(err_msg, 'error')

            return RetDict(errmsg=err_msg)




    queried = DBSession.query(Banner).filter_by(status=1)
    count = DBSession.query(Banner).filter_by(status=1).count()


    return wrap_user2(request, {'banners': queried,'count': count } )



def includeme(config):


    config.add_route('admin_home_banners','/admin/banners')
    config.add_route('admin_home_banner_add','/admin/banner/add')
    config.add_route('admin_home_banner_edit',  '/admin/banner/edit/{id}')
