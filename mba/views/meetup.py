#!/usr/bin/python
# coding: utf-8

from datetime import datetime
import re

import deform
import colander
import jinja2
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.renderers import render_to_response
from pyramid.encode import urlencode
from formencode.validators import Email
from pyramid.request import Response

from js.jquery import jquery

from kotti import get_settings
from kotti.security import get_principals
from kotti import DBSession
from kotti.security import get_user
from kotti.interfaces import IContent
from kotti.util import title_to_name

from mba.resources import MbaUser, TZ_HK, Participate, Comment, MeetupInvitation
from mba import _
from mba.utils.decorators import wrap_user
from mba.utils import wrap_user as wrap_user2
from mba.resources import Act
from mba.fanstatic import bootstrap
from mba.utils.sms import SMSSender
from mba.views.widget import PhoneValidateCodeInputWidget
from mba.utils.validators import deferred_phonecode_validator
from mba.utils import generate_unique_name_from_realname

__author__ = 'sunset'
__date__ = '20140614'


phone_re = re.compile('^\d{11}$')
def phone_pattern_validator(node, value):
    if len(value) != 11 or not phone_re.match(value):
        raise colander.Invalid(node, u"不合法的手机号")

from deform.widget import Widget




class MeetupSignupSchema(colander.MappingSchema):


    phone = colander.SchemaNode(
        colander.String(),
        title=_(u'手机'),
        validator= phone_pattern_validator,
        widget=deform.widget.TextInputWidget(number=True)
        # widget=PhoneValidateCodeInputWidget()
    )

    sms_validate_code = colander.SchemaNode(
        colander.String(),
        title=_(u"验证码"),
        validator=deferred_phonecode_validator,
        widget=PhoneValidateCodeInputWidget(inputname='phone')
    )

    real_name = colander.SchemaNode(
        colander.String(),
        title=_(u'姓名'),
    )

    company = colander.SchemaNode(
        colander.String(),
        title=_(u'公司'),
    )

    title = colander.SchemaNode(
        colander.String(),
        title=_(u'职务')
    )


def signup_validator(form, value):
    pass


def participate_meetup(meetup, user):
    part = Participate()
    part.act_id = meetup.id
    part.user_id = user.id
    DBSession.add( part )
    DBSession.flush()

@view_config(route_name='meetup_signup',  renderer='mobile/meetup_signup.jinja2')
def mobile_view_meetup_signup(context, request):

    meetupname = request.matchdict['name']
    meetup = DBSession.query(Act).filter_by(name=meetupname).first()

    if  meetup is None:
        return Response(u"不存在的活动")



    formtitle = u"活动报名:%s.." % (meetup.title[:10],)
    schema = MeetupSignupSchema(title=formtitle,
                                description=u"<a href='/login?came_from=/meetup/%s'>已有友汇网帐号？直接登陆报名</a>" % meetupname,
                                validator=signup_validator).bind(request=request)

    form = deform.Form(schema,
                       buttons=[deform.form.Button(u'submit', title=u'确认报名')

                       ],
                        )
    rendered_form = None

    bootstrap.need()


    if 'submit' in request.POST:
        try:
            appstruct = form.validate(request.POST.items())

            principals = get_principals()

            phone = appstruct['phone']

            user =  DBSession.query(MbaUser).filter(MbaUser.phone==phone, MbaUser.status!=MbaUser.BANNED).first()





            def generate_random_password(length):
                import random
                out = ''
                for i in range(length):
                    r1 = random.randint(ord('0'),ord('9'))
                    r2 = random.randint(ord('A'),ord('Z'))
                    r3  = random.randint(ord('a'),ord('z'))
                    idx = random.randint(0,2)
                    val = [r1,r2,r3][idx]

                    out += chr(val)


                return out




            if user is not None:
                # 该手机已注册
                # this phone has already registered,  and so so will ignored.
                # Just register it

                if user in meetup.parts:

                    form.error = colander.Invalid(schema, u"您已经报过名了, 不能重复报名")
                    # print 'appstruct:', appstruct
                    rendered_form = form.render(appstruct)
                    # raise ValidationFailure(form, appstruct, '')

                else:





                    sms = SMSSender(request)
                    meetuptitle = u"%s.." % meetup.title[:10] if len(meetup.title)>10 else meetup.title
                    meetuptime = meetup.meetup_start_time.strftime("%Y-%m-%d %H:%M")

                    smsret = sms.send_enrolled_meetup_sms(user.phone, user.real_name, meetuptitle, meetuptime, meetup.location)

                    message = u"恭喜您，%s，活动报名成功! 详细信息已经发您短信" % user.real_name
                    if smsret['SUCCESS'] != smsret['errcode']:
                        message = smsret['errmsg']
                        request.session.flash(message, 'danger')
                    else:
                        #报名
                        participate_meetup(meetup, user)

                        request.session.flash(message ,'success')


                    return {}

            else:
                # 该手机没有注册，生成用户，并发短信通知其密码。







                real_name = appstruct['real_name']

                name = generate_unique_name_from_realname(real_name)

                company = appstruct['company']
                title = appstruct['title']
                new_user = MbaUser(name=name, phone=phone, real_name=real_name,company=company, title=title, groups=[u'role:viewer'])

                new_user.status = MbaUser.TO_FULLFIL_DATA
                # new_user.roles = get_settings()['kotti.register.role']

                DBSession.add(new_user)
                DBSession.flush()

                random_password = generate_random_password(6)

                new_user.phone = phone
                new_user.password = get_principals().hash_password(random_password)
                DBSession.flush()

                participate_meetup(meetup, new_user)


                sms = SMSSender(request)
                meetuptitle = u"%s.." % meetup.title[:10] if len(meetup.title)>10 else meetup.title
                meetuptime = meetup.meetup_start_time.strftime("%Y-%m-%d %H:%M")

                # TODO: 正式开放注册时要发的短信如下
                # smsret = sms.send_enrolled_meetup_and_reg_success_sms({
                #     'phonenum': new_user.phone,
                #     'user_realname': new_user.real_name,
                #     'meetup_title': meetuptitle,
                #     'meetup_time': meetuptime,
                #     'meetup_loc':  meetup.location,
                #     'username': new_user.name,
                #     'password': random_password
                #
                # })
                #
                #
                # message = u"恭喜您，%s，活动报名成功! 您以后可以用手机号'%s'(或用户名'%s')和密码'%s'登陆本站!(请进站修改密码,以后一键报名)登录本站（%s）"\
                #     % (real_name, phone, name, random_password, request.application_url)
                #
                # if smsret['SUCCESS'] != smsret['errcode']:
                #     message = smsret['errmsg']
                #     request.session.flash(message, 'danger')
                # else:
                #     request.session.flash(message ,'success')


                smsret = sms.send_enrolled_meetup_sms(new_user.phone, new_user.real_name, meetuptitle, meetuptime, meetup.location)

                message = u"恭喜您，%s，活动报名成功! 详细信息已经发您短信" % new_user.real_name
                if smsret['SUCCESS'] != smsret['errcode']:
                    message = smsret['errmsg']
                    request.session.flash(message, 'danger')
                else:
                    request.session.flash(message ,'success')


                return {}



        except ValidationFailure, e:
            rendered_form = e.render()





    if rendered_form is None:
        rendered_form = form.render(request.params)

    return { 'form': rendered_form}



@view_config(name='test_view', context=IContent, renderer='meetup.jinja2')
def view_meetup(context, request):  
    jquery.need()    
    contextbody = jinja2.Markup(context.body)
    # print 'timenow ', datetime.now(TZ_HK)
    # print 'enroll time ', context.enroll_start_time
    # context.enroll_start_time = context.enroll_start_time.replace(tzinfo = TZ_HK )
    # print 'enroll time2 ', context.enroll_start_time
    # context.enroll_finish_time =  context.enroll_finish_time.replace(tzinfo = TZ_HK )
    # context.meetup_start_time = context.meetup_start_time.replace(tzinfo = TZ_HK )
    # context.meetup_finish_time= context.meetup_finish_time.replace(tzinfo = TZ_HK )
    # print 'view_meetup'
    
    self_enrolled = False
    
    user = get_user(request)  

    enroll_success = False

            
    if request.POST :
    
        if user is None:
            request.session.flash(u"请先登陆..","info")
            came_from = request.url
            return HTTPFound("/login?came_from=%s" % came_from)        
        
        if not self_enrolled and "enroll" in request.POST:
            # enroll this               


            meetup = DBSession.query(Act).get(context.id)

            sms = SMSSender(request)
            meetuptitle = u"%s.." % meetup.title[:10] if len(meetup.title)>10 else meetup.title
            meetuptime = meetup.meetup_start_time.strftime("%Y-%m-%d %H:%M")

            smsret = sms.send_enrolled_meetup_sms(user.phone, user.real_name, meetuptitle, meetuptime, meetup.location)

            # message = u"恭喜您，%s，活动报名成功! 详细信息已经发您短信" % user.real_name
            if smsret['SUCCESS'] != smsret['errcode']:
                message = smsret['errmsg']
                request.session.flash(message, 'danger')
            else:
                #报名
                participate_meetup(meetup, user)
                self_enrolled = True
                enroll_success = True


            
        elif 'submit' in request.POST:

            
            comment_content = request.params.get("meetup-comment-input")
            
            comment = Comment()
            comment.type = comment.TYPE_MEETUP
            comment.user_id = user.id
            comment.document_id = context.id 
            
            # ACTION!!!: There is a SQL injection risk here! should be prevented
            comment.content =  comment_content
            DBSession.add( comment)
            DBSession.flush()

    if user in context.parts:
        self_enrolled = True
    total_enrolled_count = len(context.parts )


    def generate_pprint_time(t1, t2):

        if t2.year != t1.year:
            pprint_out = u"%s时 至 %s时" % (t1.strftime("%Y-%m-%d %H"),  t2.strftime("%Y-%m-%d %H"))
        elif t2.month != t1.month or t2.day != t1.day:
            pprint_out = u"%s 至 %s" % (t1.strftime("%Y-%m-%d %H:%M"),  t2.strftime("%m-%d %H:%M"))
        # elif t2.day != t1.day:
        #     pprint_out = u"%s 至 %s" % (t1.strftime("%Y-%m-%d %H:%M"),  t2.strftime("%d %H:%M"))
        else:
            pprint_out = u"%s %s - %s" % (t1.strftime("%Y-%m-%d"), t1.strftime("%H:%M"),  t2.strftime("%H:%M"))

        return pprint_out



    # meetup_delta = context.meetup_finish_time - context.meetup_start_time

    pprint_time_meetup = generate_pprint_time(context.meetup_start_time, context.meetup_finish_time  )
    pprint_time_enroll = generate_pprint_time(context.enroll_start_time, context.enroll_finish_time  )

    return  wrap_user2(request, 
                {'context':context, 
                'contextbody': contextbody,
                # 'time_now': datetime.now(TZ_HK)
                'time_now': datetime.now(),
                'self_enrolled': self_enrolled,
                'enroll_success': enroll_success,
                'comments_count': len(context._comments),
                'pprint_time_meetup': pprint_time_meetup,
                'pprint_time_enroll': pprint_time_enroll,
                'total_enrolled_count': total_enrolled_count                
                })


def includeme(config):
    config.add_route('meetup','/meetup')
    config.add_route('meetup_signup','/meetup/{name}/signup')

    config.scan(__name__)
