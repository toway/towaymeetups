#!/usr/bin/python
# coding: utf-8

from datetime import datetime
from sqlalchemy.orm import class_mapper
from kotti import DBSession
from kotti import get_settings
import transaction
from kotti.security import get_principals
from kotti.resources import get_root
from kotti.resources import Node
from kotti.security import SITE_ACL

from mba.resources import *

# Just test hear, TODO for auto tests
_TEST_ATTRS = dict(
    title=u'Test Act',
    name=u'Just Test',
    description=u'Our company is the leading manufacturer of foo widgets used in a wide variety of aviation and and industrial products.',
    body=u"<p>Hello</p>",
    status=ActStatus.DRAFT,
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
    p = Position(
            job_name=u'软件工程师',
            company_name=u'公务员',
            degree=u'本科文凭',
            experience=u'三年以上',
            salary=10000,
            parent_id = get_root(),
            **_TEST_ATTRS)
    DBSession.add(p)
    #DBSession.flush()
    #print p.id

    stu = DBSession.query(MbaUser).filter_by(email='a@gmail.com').first()
    stu.interests = ['haha','oooo','ddd']
    stu.positions = [p]
    DBSession.flush()
    print stu.position_items

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

def create_mba_root():
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
        node1 = MeetupType(title=u"聚友沙龙")        
        node2 = MeetupType(title=u"志友下午茶")        
        node3 = MeetupType(title=u"私人董事会")        
        node4 = MeetupType(title=u"志友健康行")        
        DBSession.add(node1)        
        DBSession.add(node2)        
        DBSession.add(node3)        
        DBSession.add(node4)        

    if DBSession.query(Student).count() == 0:
        DBSession.add(Student(name="testmba",password="123456",email="1@1.com",real_name=u'陈测试'))

        

def populate():
    create_mba_root()

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
    #test_position()
