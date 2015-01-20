#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'sunset'
__date__ = '20141111'

import datetime
import random
import urllib2
import urllib
import json
from mba.utils import RetDict
from mba.security import DBSession
from mba.resources import ValidationSms

class SMSServiceProvider(object):
    def __sendsms(self, phonenum):
        raise NotImplementedError

    def send_validate_sms(self, phonenum, code):
        raise NotImplementedError

    def send_reg_success_sms(self, phonenum, user_realname, username, password ):
        raise NotImplementedError

    def send_enrolled_meetup_and_reg_success_sms(self, options):
        raise NotImplementedError


class GuanXin(SMSServiceProvider):

    URL = "http://denglu.guanxinapp.com/send_text.ext"

    CONTENT_TEMPLATE = "您的验证码是：%s。请不要把验证码泄露给其他人。"


    def sendsms(self, phonenum, code):
        req = urllib2.Request(self.URL)
        req.add_header('X-Send-Text','cascade')
        req.add_header('X-Ajax-Header','ajax-post')
        req.add_header('X-Requested-With','XMLHttpRequest')
        req.add_data(urllib.urlencode({'mobile':phonenum,'content': self.CONTENT_TEMPLATE % code}))


        # print req



        res = urllib2.urlopen(req)
        response = res.read()
        resobj = json.loads(response)

        return resobj

class FeiTuo(SMSServiceProvider):
    URL = "http://222.185.228.25:8000/msm/sdk/http/sendsmsutf8.jsp" #?username=NTY000000&scode=123456&mobile=13805100000&content=你好101540"
    USERNAME = "XFTB702041"
    PASSWORD = "238233"
    # CONTENT_TEMPLATE = "您的验证码为:%s。【MBA友汇网】"
    TEMPLATE_ID_VALIDATE  = "MB-2013102300" #你好，你的验证码为：@1@。
    TEMPLATE_ID_ENROLL_MEETUP  = "MB-2015011413" #@1@您好，您已经成功报名活动@2@，请您于@3@准时抵达@4@参加活动。
    TEMPLATE_ID_REG_SUCCESS = "MB-2015011458" #@1@您好，欢迎来到友汇网，您以后可以直接用手机号(或用户名@2@)和密码@3@登陆。
    TEMPLATE_ID_ENROLL_MEETUP_AND_REG = "MB-2015011447" #@1@您好，您已经成功报名活动@2@，请您于@3@准时抵达@4@参加活动。您以后可以直接用手机号(或用户名@5@)和密码@6@登陆友汇网。
    TEMPLATE_ID_AUTH_PASS = "MB-2015012050" #您好，您的资料已经通过友汇网认证，来友汇网结识专家、高管、更多MBAer吧！
    DEFAULT_OPTIONS = {
        'username':USERNAME,
        'scode':PASSWORD,
    }

    ERROR_MAP = {
        100	: u'发送失败',
        101	: u'用户账号不存在或密码错误',
        102	: u'账号已禁用',
        103	: u'参数不正确',
        105	: u'短信内容超过500字、或为空、或内容编码格式不正确',
        106	: u'手机号码超过100个或合法的手机号码为空，每次最多提交100个号',
        108	: u'余额不足',
        109	: u'指定访问ip地址错误',
        #110#(敏感词A,敏感词B)	短信内容存在系统保留关键词，如有多个词，使用逗号分隔：110#(李老师,成人)
        110 : u'短信内容存在系统保留关键词',
        114	: u'模板短信序号不存在',
        115	: u'短信签名标签序号不存在'
    }

    def __sendsms(self,  options):

        def encoded_dict(in_dict):
            out_dict = {}
            for k, v in in_dict.iteritems():
                if isinstance(v, unicode):
                    v = v.encode('utf8')
                elif isinstance(v, str):
                    # Must be encoded in UTF-8
                    v.decode('utf8')
                out_dict[k] = v
            return out_dict

        self.DEFAULT_OPTIONS.update( options  )
        options= self.DEFAULT_OPTIONS
        req = urllib2.Request(self.URL)
        print options

        if options.get('mobile',None) is None or len(options['mobile'])!=11:
            return RetDict(errmsg=u"不合法的手机号码")

        req.add_data(urllib.urlencode(encoded_dict(options)))
        res = urllib2.urlopen(req)
        response = res.read().strip()
        resarr = response.split('#')
        if resarr[0] == '0':
            return RetDict(retval=u'发送成功')
        else:
            errmsg = self.ERROR_MAP[int(resarr[0])]
            # print errmsg
            if resarr[0] == '110':
                print  resarr[1]

                # errmsg =  u'%s:%s' % (errmsg, resarr[1] )

            return RetDict(errmsg=errmsg)

    def send_auth_pass_sms(self, phonenum):
        options = {
            'mobile':phonenum,
            'tempid': self.TEMPLATE_ID_AUTH_PASS,
            'content': ''
        }
        return self.__sendsms( options)


    def send_validate_sms(self, phonenum, code):
        options = {
            'mobile':phonenum,
            'tempid': self.TEMPLATE_ID_VALIDATE,
            'content': "@1@=%s" % code}
        return self.__sendsms( options)

    def send_enrolled_meetup_sms(self, phonenum, user_realname, meetup_title, meetup_time, meetup_loc):
        content = u"@1@=%s,@2@=%s,@3@=%s,@4@=%s" % (user_realname, meetup_title, meetup_time, meetup_loc)
        options = {
            'mobile':phonenum,
            'tempid': self.TEMPLATE_ID_ENROLL_MEETUP,
            'content':  content
        }
        return self.__sendsms(options)

    def send_reg_success_sms(self, phonenum, user_realname, username, password ):
        content = u"@1@=%s,@2@=%s,@3@=%s" % (user_realname, username, password)
        options = {
            'mobile':phonenum,
            'tempid': self.TEMPLATE_ID_REG_SUCCESS,
            'content':  content
        }
        return self.__sendsms(options)

    def send_enrolled_meetup_and_reg_success_sms(self, options):
        o = options
        user_realname = o['user_realname']
        meetup_title = o['meetup_title']
        meetup_time = o['meetup_time']
        meetup_loc = o['meetup_loc']
        phonenum = o['phonenum']
        username = o['username']
        password = o['password']
        content = u"@1@=%s,@2@=%s,@3@=%s,@4@=%s,@5@=%s,@6@=%s" % \
                  (user_realname, meetup_title, meetup_time, meetup_loc,  username, password)
        options = {
            'mobile':phonenum,
            'tempid': self.TEMPLATE_ID_ENROLL_MEETUP_AND_REG,
            'content':  content
        }
        return self.__sendsms(options)


test = False
if test:
    f = FeiTuo()
    out = f.send_enrolled_meetup_sms('18666665393', u'蒋小良', u'杀之夜', '2015-01-15',u'园博园')
    print out




# def sendsmscore(phonenum, code):
#
#
#
#
#     o = GuanXin()
#     try:
#         res = o.sendsms(phonenum, code)
#     except Exception,ex:
#         res = {'success': False, 'errors': "%s" % ex }
#
#     if res['success'] is True:
#         return RetDict(retval=u"发送成功")
#     else:
#         return RetDict(errmsg=res['errors'])
#


class SMSSender(object):

    def __init__(self, request, is_test = False):
        self.smsobj = FeiTuo()
        self.is_test = is_test
        self.request = request

    def send_auth_pass_sms(self, phonenum):
        error =  self.protect( phonenum)
        if error:
            return error

        result = self.smsobj.send_auth_pass_sms(phonenum)

        if result['errcode'] == result['SUCCESS']:
            # Send ok, write to the DB
            rsms = ValidationSms(phonenum=phonenum, validate_code='auth_pass', ip=self.request.remote_addr)
            DBSession.add(rsms)

        return result

    def send_validate_sms(self, phonenum):

        error =  self.protect( phonenum)
        if error:
            return error

        code = self.generate_random_code()

        # To deploy
        if not self.is_test:
            result = self.smsobj.send_validate_sms(phonenum=phonenum, code=code)
        else:
            # for test purpose only below
            result = RetDict(retval={'istest':True,'code':code})


        if result['errcode'] == result['SUCCESS']:
            # Send ok, write to the DB
            rsms = ValidationSms(phonenum=phonenum, validate_code=code, ip=self.request.remote_addr)
            DBSession.add(rsms)

            self.request.session['sms_validate_code'] = code
            # TODO: setup pyramid-beaker to expire the validate_code in 5 miniutes(more or less)

        return result


    def send_enrolled_meetup_sms(self, phonenum, user_realname, meetup_title, meetup_time, meetup_loc):
        error =  self.protect( phonenum)
        if error:
            return error

        code = self.generate_random_code()

        # To deploy
        if not self.is_test:
            result = self.smsobj.send_enrolled_meetup_sms(phonenum, user_realname, meetup_title, meetup_time, meetup_loc)
        else:
            # for test purpose only below
            result = RetDict(retval={'istest':True,'code':code})

        if result['errcode'] == result['SUCCESS']:
            # Send ok, write to the DB
            rsms = ValidationSms(phonenum=phonenum, validate_code='enrolled_meetup', ip=self.request.remote_addr)
            DBSession.add(rsms)

        return result


    def send_reg_success_sms(self, phonenum, user_realname, username, password ):
        error =  self.protect( phonenum)
        if error:
            return error

        result = self.smsobj.send_reg_success_sms(phonenum, user_realname, username, password)

        if result['errcode'] == result['SUCCESS']:
            # Send ok, write to the DB
            rsms = ValidationSms(phonenum=phonenum, validate_code='reg_success', ip=self.request.remote_addr)
            DBSession.add(rsms)

        return result



    def send_enrolled_meetup_and_reg_success_sms(self,  options):
        error =  self.protect(options['phonenum'])
        if error:
            return error

        result = self.smsobj.send_enrolled_meetup_and_reg_success_sms(options)

        if result['errcode'] == result['SUCCESS']:
            # Send ok, write to the DB
            rsms = ValidationSms(phonenum=options['phonenum'], validate_code='reg_success', ip=self.request.remote_addr)
            DBSession.add(rsms)

        return result




    def protect(self,  phonenum):

       # TO protect the server from SMS attack,

        request = self.request
        now = datetime.datetime.now(tz=None)

        # 如果该IP在过去30min内尝试10次以上发送SMS， 封禁此IP
        ip =  request.remote_addr
        ips = DBSession.query(ValidationSms).filter_by(ip=ip).order_by(ValidationSms.id).all()

        if len(ips) >= 10 and ( now - ips[9].send_datetime).seconds < 30 * 60:
            return RetDict(errmsg=u"请务非法操作!")



        smss = DBSession.query(ValidationSms).filter_by(phonenum=phonenum).order_by(ValidationSms.id).all()




        if len(smss) != 0:
            # TODO: this should be configurable
            if len(smss) >= 20:
                return RetDict(errmsg=u"该手机号尝试注册超过20次,永远封禁!")


            last_send_time = smss[0].send_datetime


            if (now - last_send_time).seconds < 60 : # 距上次发送间隔小于60秒
                return RetDict(errmsg=u"这样灌水也是挺累的,请歇息一会儿吧")

            sended_in_24hour = 0
            for sms in smss:
                if (now - sms.send_datetime).seconds <= 24*60*60: # less then One day
                    sended_in_24hour += 1
                else:
                    break

            if sended_in_24hour >= 5:
                return RetDict(errmsg=u"过去24小时累计发送超过5次,请休息一会儿吧")






    def generate_random_code(self):
        return str(random.randint(1000,9999) )




