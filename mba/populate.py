#!/usr/bin/python
# coding: utf-8

import os
import codecs
from datetime import datetime
from sqlalchemy.orm import class_mapper
from kotti import DBSession
from kotti import get_settings
import transaction
from kotti.security import get_principals
from kotti.resources import get_root
from kotti.resources import Node
from kotti.security import SITE_ACL
import json
from xpinyin import Pinyin

from mba.resources import *

# Just test hear, TODO for auto tests
_TEST_ATTRS = dict(
    title=u'Test Act',
    name=u'Just Test',
    description=u'Our company is the leading manufacturer of foo widgets used in a wide variety of aviation and and industrial products.',
    body=u"<p>Hello</p>",
    status=Act.STATUS_DRAFT,
    )

def test_document():
    print 'Test Act'
    print DBSession.query(Act).count()
    act = Act(**_TEST_ATTRS)
    DBSession.add(act)
    print DBSession.query(Act).count()
    act.tags = [u'tag 1', u'tag 2']
    DBSession.flush()
    act = DBSession.query(Act).first()
    print act.tags
    print act._tags
    for t in act._tags:
        print t.item, 

def test_act():
    # Step 1 Act test
    print 'Test Act'
    print DBSession.query(Act).count()
    act = Act(**_TEST_ATTRS)
    DBSession.add(act)
    print DBSession.query(Act).count()
    print 'Act.parts', act.parts

    # Step 2 Student test
    print 'Test Student'
    print DBSession.query(Student).count()
    stu = Student(name=u'test')
    DBSession.add(stu)
    print DBSession.query(Student).count()

    # Step 3 Participate test
    part = Participate()
    part.act_id = act.id
    part.user_id = stu.id
    DBSession.add(part)
    print 'Act.parts', act.parts
    DBSession.flush()
    #part = DBSession.query(Participate).first()
    #print 'Part user', part.user, part.act_id
    act = DBSession.query(Act).first()
    print 'query Act', act.id
    print 'Act.parts', act._parts


def test_act2():
    stu = Student(name=u'test', real_name=u'testit')
    DBSession.add(stu)

    a = Act(**_TEST_ATTRS)
    p = Participate()
    p.user = stu
    a._parts.append(p)
    DBSession.add(a)
    DBSession.flush()
    act = DBSession.query(Act).first()
    print 'query Act', act.id
    print 'Act.parts', act.parts
    print 'student.real_name: ', act.parts[0].real_name

def test_city():
    act = Act(**_TEST_ATTRS)
    act.city = City(name='Shenzhen')
    DBSession.add(act)
    act = DBSession.query(Act).first()
    print 'act city title', act.city_name

def test_friend():
    #u1,u2,u3,u4,u5 = MbaUser(u'u1'), MbaUser(u'u2'), MbaUser(u'u3'), \
    #        MbaUser(u'u4'), MbaUser(u'u5')
    u1,u2,u3,u4,u5 = Student(u'u1'), Student(u'u2'), Student(u'u3'), \
            Student(u'u4'), Student(u'u5')
    u1.friends = [u2, u3]
    u4.friends = [u2, u5]
    u3.friends.append(u5)
    DBSession.add_all([u1,u2,u3,u4,u5])
    DBSession.flush()
    print 'u2 all', u2.all_friends
    print 'u5 all', u5.all_friends

def test_resume():
    stu = Student(name=u'test', real_name=u'testit')
    DBSession.add(stu)
    skill1, skill2 = Skill(name=u'python'), Skill(name=u'c++')
    resume1 = Resume(title=u'resume1', user=stu)
    resume1.skills = [skill1.name, skill2.name]
    DBSession.add(resume1)
    DBSession.flush()

    resume2 = Resume(title=u'resume2', user=stu)
    resume2.skills = [skill1.name, skill2.name]
    DBSession.add(resume2)
    skill = DBSession.query(Skill).first()
    print skill.resumes

def test_user():
    u = MbaUser(name=u'test')
    DBSession.add(u)
    stu = Student(name=u'test2', real_name=u'testit2')
    DBSession.add(stu)
    DBSession.flush()

    #print 'stu type', stu.type
    #print u.__class__, u.type
    u.__class__ = Student
    u.type = 'student'
    DBSession.execute("insert into students (id,real_name) values (%d,'error_name');" % u.id)
    DBSession.flush()
    
    u2 = DBSession.query(MbaUser).filter_by(name=u'test').first()
    print u2
    #DBSession.query(Student).filter_by(id=u.id).update({'id':u.id,'real_name':'ooooooo'}, synchronize_session=False)
    u2.real_name='bbbbbbbbbbb'
    DBSession.flush()

    u3 = DBSession.query(Student).filter_by(name=u'test').first()
    print u3.real_name
    #mapper._identity_class = mapper.inherits._identity_class

def test_add_stu():
    settings = get_settings()
    appstruct = {}
    register_groups = settings['kotti.register.group']
    if register_groups:
        appstruct['groups'] = [register_groups]
    register_roles = settings['kotti.register.role']
    if register_roles:
        appstruct['roles'] = set(['role:' + register_roles])
    name = u'方程程'
    appstruct['name'] = name
    appstruct['email'] = 'a@gmail.com'
    appstruct['last_login_date'] = datetime.now(TZ_HK)
    appstruct['password'] = 'asdfgh'
    stu = Student(**appstruct)
    DBSession.add(stu)

    user = get_principals()[name]
    user.password = get_principals().hash_password(appstruct['password'])

    DBSession.flush()

def test_resume2():
    stu = DBSession.query(MbaUser).filter_by(email='a@gmail.com').first()
    resume1 = Resume(title=u'resume1', user=stu)
    start_date = datetime.strptime('2003-1-1','%Y-%m-%d').date()
    finish_date = datetime.strptime('2008-1-1','%Y-%m-%d').date()
    edu = Education(
            school_name = u'电子科技大学',
            start_date=start_date,
            finish_date=finish_date,
            major=u'通信工程',
            degree = 1)
    resume1.educations.append(edu)

    job = Job(
            industy = u'美丽的台湾公司',
            industy_type = 1,
            industy_scale = 1,
            duty = u'软件工程师',
            start_date = start_date,
            finish_date = finish_date,
            )
    resume1.jobs.append(job)

    DBSession.add(resume1)
    DBSession.flush()

def test_position():
    if DBSession.query(Position).count() == 0:
        p = Position(
                degree=u'本科文凭',
                experience=u'三年以上',
                salary=10000,
                city_name=u"北京",
                location=u"北京三环路",
                company_id = 1,
                parent_id = get_root().id,
                title=u"高级销售经理",
                name=u"高级销售经理",
                description=u'我们公司很需要这方面的人才',
                body=u"<p>我们公司很需要这方面的人才</p>",
                status=Position.STATUS_DRAFT,
                )
        DBSession.add(p)
        DBSession.flush()
        print p.id

    #stu = DBSession.query(MbaUser).filter_by(email='a@gmail.com').first()
    #stu.interests = ['haha','oooo','ddd']
    #stu.positions = [p]
    #DBSession.flush()
    #print stu.position_items

def test_visitors():
    stu1 = Student(name=u'test1', real_name=u'testit1')
    stu2 = Student(name=u'test2', real_name=u'testit2')
    stu3 = Student(name=u'test3', real_name=u'testit3')
    DBSession.add(stu1)
    DBSession.add(stu2)
    DBSession.add(stu3)
    DBSession.flush()

    stu2.add_visit(stu1)
    stu2.add_visit(stu3)
    print stu2.visitors

def populate_interests():
    if DBSession.query(Interest).count() == 0:
        inter = [u"唱歌/K歌",u"听音乐",u"看电影",u"看韩剧/综艺娱乐节目",u"看书/小说/杂志",u"逛街/购物",u"跳舞",u"演奏乐器",
                 u"去健身房健身/减肥/塑形/瑜伽",u"打篮球",u"踢足球",u"打排球",u"跑步",u"打羽毛球",u"打乒乓球",u"保龄球",
                 u"高尔夫",u"远足",u"爬山/登山",u"X运动",u"游泳",u"划船/水上娱乐",u"钓鱼/养鱼",u"饲养宠物",u"玩网络游戏/单机游戏",
                 u"上网聊天/论坛/贴吧",u"看新闻",u"摄影/摄像",u"旅游",u"吃美食/做饭",u"十字绣/织毛衣/做服装服饰",u"打扑克/麻将",
                 u"写字/练字/书法",u"下棋/各种棋",u"睡觉",u"美容/保养/化妆/打扮"]
        for int in inter:
            io = Interest(name=int)
            DBSession.add(io)


        DBSession.flush()



def create_mba_root():
    populate_interests()
    if DBSession.query(Node).filter_by(name="meetup").count() == 0:
        meet_attrs = dict(
            title=u'meetup',
            name=u'meetup',
            description=u'The root of meetup',
            body=u"<p>Hello meetup</p>",
            parent_id = get_root().id,
        )
        root = Document(**meet_attrs)
        root.__acl__ = SITE_ACL
        DBSession.add(root)
        
    if DBSession.query(Node).filter_by(name="review").count() == 0:
        meet_attrs = dict(
            title=u'review',
            name=u'review',
            description=u'The root of review',
            body=u"<p>Hello review</p>",
            parent_id = get_root().id,
        )
        root = Document(**meet_attrs)
        root.__acl__ = SITE_ACL
        DBSession.add(root)        
    if DBSession.query(Node).filter_by(name="job").count() == 0:
        job_attrs = dict(
            title=u'job',
            name=u'job',
            description=u'The root of job',
            body=u"<p>Hello job</p>",
            parent_id = get_root().id,
        )
        root = Document(**job_attrs)
        root.__acl__ = SITE_ACL
        DBSession.add(root)
    if DBSession.query(Node).filter_by(name="position").count() == 0:
        job_attrs = dict(
            title=u'position',
            name=u'position',
            description=u'The root of position',
            body=u"<p>Hello Position</p>",
            parent_id = get_root().id,
        )
        root = Document(**job_attrs)
        root.__acl__ = SITE_ACL
        DBSession.add(root)
    if DBSession.query(Node).filter_by(name="images").count() == 0:
        meet_attrs = dict(
            title=u'images',
            name=u'images',
            description=u'The root of images',
            body=u"<p>images</p>",
            parent_id = get_root().id,
        )
        root = Document(**meet_attrs)
        root.__acl__ = SITE_ACL
        DBSession.add(root)


    # TODO: Make this addable and  editable
    if DBSession.query(MeetupType).count() == 0:        
        node1 = MeetupType(title=u"官方活动")
        node2 = MeetupType(title=u"外部活动")

        DBSession.add(node1)        
        DBSession.add(node2)        


    if DBSession.query(Student).count() == 0:
        DBSession.add(Student(name="testmba",title=u"创始人", password="123456",email="1@1.com",real_name=u'陈测试',city_name=u'深圳', school=u'斯坦福大学', groups=[u'role:admin', u'role:owner', u'role:editor', u'role:viewer']))
        testmba2 = Student(name="testmba2",title=u"总监",password="123456",email="2@1.com",real_name=u'余软件',city_name=u'北京', school=u'斯坦福大学', groups=[u'role:admin', u'role:owner', u'role:editor', u'role:viewer'])
        DBSession.add(testmba2)
        DBSession.add(Student(name="testmba3",title=u"副总裁",password="123456",email="3@1.com",real_name=u'羊前端',city_name=u'上海', school=u'斯坦福大学', groups=[u'role:owner',u'role:editor',u'role:viewer']))
        DBSession.add(Student(name="testmba4",title=u"财务官",password="123456",email="4@1.com",real_name=u'张平面',city_name=u'广州', school=u'斯坦福大学', groups=[u'role:viewer']))


    if DBSession.query(Node).filter_by(name="infomation").count() == 0:
        info_attrs = dict(
            title=u'Infomations',
            name=u'infomation',
            description=u'The root of infomations',
            body=u"<p>infomations</p>",
            parent_id = get_root().id,
        )
        root = Document(**info_attrs)
        root.__acl__ = SITE_ACL
        DBSession.add(root)

def create_univs():
    if DBSession.query(Univs).count() == 0:
        p = Pinyin()
        univs_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "univs.txt")
        with codecs.open(univs_path, "r", "utf8") as unvis_file:
            for line in unvis_file:
                line = line[0:len(line)-1]
                cc = '#'
                py = p.get_pinyin(line, cc)
                p1 = ""
                p2 = ""
                if cc in py:
                    p2 = ''.join([c[0] for c in py.split(cc)])
                    p1 = py.replace(cc,'')
                u = Univs(name=line, pinyin=p1, pprev=p2)
                DBSession.add(u)
        DBSession.flush()

def populate():
    if DBSession.query(CompanyInfo).count() == 0:
        c = CompanyInfo(name=u"深圳市芭田生态工程股份有限公司"
            , scope=u"1000-2000人"
            , industry=u"农林"
            , type_info=u"民营"
            , location=u"南山区前海路"
            , description=u"深圳市芭田生态工程股份有限公司是一家非常好的公司啊")
        DBSession.add(c)
        DBSession.flush()

    create_mba_root()
    create_univs()

    print 'Just test in mba.resources: '
    #test_visitors()
    #test_document()
    #test_act()
    #test_act2()
    #test_city()
    #test_friend()
    #test_user()
    #test_add_stu()
    #test_resume2()
    test_position()
