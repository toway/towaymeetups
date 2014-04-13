from kotti import DBSession
from kotti import get_settings
from kotti.security import get_principals
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
    city = City(name='Shenzhen')
    act = Act(**_TEST_ATTRS)
    act.city = city
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

def test_add_stu():
    settings = get_settings()
    appstruct = {}
    register_groups = settings['kotti.register.group']
    if register_groups:
        appstruct['groups'] = [register_groups]
    register_roles = settings['kotti.register.role']
    if register_roles:
        appstruct['roles'] = set(['role:' + register_roles])
    name = 'auto_add_user'
    appstruct['name'] = name
    appstruct['email'] = 'a@gmail.com'
    appstruct['last_login_date'] = datetime.now()
    appstruct['password'] = 'asdfgh'
    stu = Student(**appstruct)
    DBSession.add(stu)

    user = get_principals()[name]
    user.password = get_principals().hash_password(appstruct['password'])

    DBSession.flush()

def populate():
    print 'Just test in mba.resources: '
    #test_document()
    #test_act()
    #test_act2()
    #test_city()
    #test_friend()
    #test_resume()
    #test_add_stu()
