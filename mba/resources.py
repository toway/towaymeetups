# coding: utf-8

import os
from UserDict import DictMixin
from fnmatch import fnmatch
from datetime import datetime
from datetime import date
import pytz

from pyramid.threadlocal import get_current_registry
from pyramid.traversal import resource_path
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime, Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, Float
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
from sqlalchemy import Table, select
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import backref
from sqlalchemy.orm import deferred
from sqlalchemy.orm import object_mapper
from sqlalchemy.orm import relation, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import and_
from sqlalchemy.sql import select
from sqlalchemy.util import classproperty
from transaction import commit
from zope.deprecation.deprecation import deprecated
from zope.interface import implements

import kotti
from kotti import Base
from kotti import DBSession
from kotti import get_settings
from kotti import metadata
from kotti.interfaces import INode
from kotti.interfaces import IContent
from kotti.interfaces import IDocument
from kotti.interfaces import IFile
from kotti.interfaces import IImage
from kotti.interfaces import IDefaultWorkflow
from kotti.migrate import stamp_heads
from kotti.security import PersistentACLMixin
from kotti.security import has_permission
from kotti.security import view_permitted, SITE_ACL
from kotti.security import Principals, get_principals
from kotti.sqla import ACLType
from kotti.sqla import JsonType
from kotti.sqla import MutationList
from kotti.sqla import NestedMutationDict
from kotti.util import ViewLink
#from kotti.util import _
from kotti.util import camel_case_to_name
from kotti.util import get_paste_items
from kotti.util import camel_case_to_name
from kotti.resources import Document

from mba import _

TZ_HK = pytz.timezone('Asia/Hong_Kong')

friend = Table(
        'friends', Base.metadata,
        Column('user_a_id', Integer, ForeignKey('mba_users.id'), primary_key=True),
        Column('user_b_id', Integer, ForeignKey('mba_users.id'), primary_key=True),
        Column('status', Integer, default=0)  # 0: No friend yet, 1: friend already
        )

# Meetup Invitation
class MeetupInvitation(Base):
     id = Column('id', Integer, nullable=False,  primary_key=True, autoincrement=True)
     inviter_id = Column('inviter_id',Integer, ForeignKey('mba_users.id'))     #邀请者
     inviter = relationship("MbaUser", foreign_keys="[MeetupInvitation.inviter_id]")
     invitee_id = Column('invitee_id', Integer, ForeignKey('mba_users.id') )     #被邀请者
     invitee = relationship("MbaUser", foreign_keys="[MeetupInvitation.invitee_id]")

     meetup_id = Column(Integer, ForeignKey('acts.id'))
     meetup =  relationship('Act')


     status = Column(Integer, default=0) # 0 : unread, 1: ignore 2:accept, 3: reject 4: deleted



class UserInterest(Base):
    interest_id = Column(Integer, ForeignKey('interests.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('mba_users.id'), primary_key=True)
    # interest = relationship('Interest', backref='interest_items')
    # name = association_proxy('interest', 'name')

    user = relationship("MbaUser",
                        backref=backref("user_interests",
                                        cascade="all, delete-orphan")
                        )
    interest = relationship("Interest")
    interest_name = association_proxy("interest", "name")

    @classmethod
    def _interest_find_or_create(cls, name):
        with DBSession.no_autoflush:
            interest = DBSession.query(Interest).filter_by(name=name).first()
        if interest is None:
            interest = Interest(name=name)
        return cls(interest=interest)

class UserSkill(Base):
    interest_id = Column(Integer, ForeignKey('interests.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('mba_users.id'), primary_key=True)


    user = relationship("MbaUser",
                        backref=backref("user_skills",
                                        cascade="all, delete-orphan")
                        )
    skill = relationship("Interest")
    skill_name = association_proxy("skill", "name")

    @classmethod
    def _interest_find_or_create(cls, name):
        with DBSession.no_autoflush:
            interest = DBSession.query(Interest).filter_by(name=name).first()
        if interest is None:
            interest = Interest(name=name)
        return cls(skill=interest)



class Interest(Base):
    __table_args__ = (
        UniqueConstraint('name'),
        )
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    description = Column(UnicodeText())

    def __init__(self, name, **kw):
        self.name = name
        Base.__init__(self,**kw)

    # def __repr__(self):
    #     return (self.name)

    @property
    def users(self):
        return [rel.user for rel in self.interest_items]

#TODO for deleting
class PositionCollect(Base):
    position_id = Column(Integer, ForeignKey('positions.id', ondelete='cascade'), primary_key=True)
    user_id = Column(Integer, ForeignKey('mba_users.id', ondelete='cascade'), primary_key=True)
    create_date = Column(DateTime(), default=datetime.now(tz=None))
    position = relationship('Position', backref='position_items')

    @classmethod
    def _create(cls, p):
        if p is None:
            raise Exception('position can not be None')
        return cls(position=p)

class Visit(Base):
    user_id1 = Column('user_id1', Integer, ForeignKey('mba_users.id'), primary_key=True)
    user_id2 = Column('user_id2', Integer, ForeignKey('mba_users.id'), primary_key=True)
    visit_date = Column(DateTime(), default=datetime.now(tz=None))

    # 1 <--> 1
    user = relationship("MbaUser", foreign_keys="[Visit.user_id2]")


class City(Base):
    __tablename__ = 'city'
    __table_args__ = (
        UniqueConstraint('name'),
        )
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), nullable=False)
    acts = relationship("Act", backref='city', order_by='desc(Act.creation_date)')
    usercity = relationship("MbaUser", backref='city', order_by='desc(MbaUser.creation_date)')

    @classmethod
    def _find_or_create(cls, name):
        with DBSession.no_autoflush:
            obj = DBSession.query(City).filter_by(name=name).first()
        if obj is None:
            obj = City(name=name)
            # print 'cannt find city create one'
        #return cls(city=obj)
        return obj

class UserBetween(Base):
    city_id = Column(Integer, ForeignKey('city.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('mba_users.id'), primary_key=True)


    user = relationship("MbaUser",
                        backref=backref("user_between",
                                        cascade="all, delete-orphan")
                        )
    city = relationship("City")
    city_name = association_proxy("city", "name")

    @classmethod
    def _city_find_or_create(cls, name):
        city = City._find_or_create(name=name)
        return cls(city=city)

class Message(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)

    sender_id = Column(Integer, ForeignKey('mba_users.id'))
    sender = relationship("MbaUser", foreign_keys="[Message.sender_id]")

    reciever_id = Column(Integer, ForeignKey('mba_users.id'))
    reciever = relationship("MbaUser", foreign_keys="[Message.reciever_id]")


    # message type,
    # 0: system message
    # 1: admin message
    # 2: friend private message
    # 10: somebody ask to be friend
    # 11: friends invite  me some person
    # 12: friends invite me some meetup

    type = Column(Integer)
    content =  Column(String(500))

    status = Column(Integer,default=0) # 0: unread, 1:read, 2:deleted

from mba.utils import assign_default_avatar

#This is a base class for all users
class MbaUser(Base):

    __mapper_args__ = dict(
        order_by='mba_users.id',
        # polymorphic_on='type',
        # polymorphic_identity='mba_users',
        #with_polymorphic='*',
        )

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), unique=True)
    password = Column(Unicode(100))

    real_name = Column(Unicode(50))

    _avatar = Column(String(100))

    @property
    def avatar(self):
        if not self._avatar:
            assign_default_avatar(self)
        return self._avatar

    @avatar.setter
    def avatar(self, value):
        self._avatar = value



    [INACTIVE,  ACTIVE, TO_FULLFIL_DATA, BANNED] = [0, 1, 2, 9999] #未激活、激活、待完善资料、禁封
    
    status = Column(Integer, default=INACTIVE)

    confirm_token = Column(Unicode(100))
    phone = Column(String(20))
    phone_privacy_level = Column(Integer, default=5) ## 1: 对所有会员公开 5: 成功交换名片可看,  9: 完全保密
    title = Column(Unicode(100), nullable=True)
    title_privacy_level =  Column(Integer, default=5) # 1: 对所有会员公开 5: 成功交换名片可看,  9: 完全保密
    email = Column(Unicode(100), unique=True)
    email_privacy_level =  Column(Integer, default=5) # 1: 对所有会员公开 5: 成功交换名片可看,  9: 完全保密
    groups = Column(JsonType(), nullable=True)
    creation_date = Column(DateTime(), nullable=True)
    last_login_date = Column(DateTime())

    [MALE, FEMALE] = range(2)
    sex = Column(Integer())

    # type = Column(String(50), nullable=True) # change type string to integer by sunset 2015.1.27
    [USER_TYPE_MBA, USER_TYPE_EMBA, USER_TYPE_MANAGER, USER_TYPE_EXPERT] = range(4)
    type = Column(Integer, default=USER_TYPE_MBA)

    
    # _interests = relationship("UserInterest", backref='user')
    interests = association_proxy(
        'user_interests',
        'interest_name',
        creator=UserInterest._interest_find_or_create,
        )
    special_skills = association_proxy(
        'user_skills',
        'skill_name',
        creator=UserSkill._interest_find_or_create,
        )
    between = association_proxy(
        'user_between',
        'city_name',
        creator=UserBetween._city_find_or_create,
        )

    company = Column(String(255), default=u"")
    company_privacy_level =  Column(Integer, default=1) # 1: 对所有会员公开 5: 成功交换名片可看,  9: 完全保密
    industry = Column(String(255), default=u"")
    # special_skill = Column(String(255), default=u"")
    interest = Column(String(255), default=u"") # job interest
    # between = Column(String(255), default=u"")
    introduction = Column(String(255), default=u"")

    _positions = relationship("PositionCollect", backref='user')
    positions = association_proxy("_positions","position", creator=PositionCollect._create)

    #http://stackoverflow.com/questions/17252816/create-many-to-many-on-one-table
    #http://docs.sqlalchemy.org/en/rel_0_8/orm/relationships.html#adjacency-list-relationships
    #visit = relationship("Visit", foreign_keys="[Visit.user_id2]", backref='users', order_by='desc(Visit.visit_date)')
    # 1 <--> 1
    visit = relationship("Visit", primaryjoin="and_(MbaUser.id==Visit.user_id1)"
            , order_by='desc(Visit.visit_date)')
    # 1 <--> n
    visitors = association_proxy("visit", "user")


    #
    friendship = relationship("MbaUser", secondary=friend,
                primaryjoin=id==friend.c.user_a_id,
                secondaryjoin=id==friend.c.user_b_id)



    invited_meetups  = relationship("MeetupInvitation",
                                    foreign_keys="[MeetupInvitation.invitee_id]" )


    messages = relationship('Message',foreign_keys="[Message.reciever_id]")
    # newmessages = Message.query.filter(status=10).count()
    newmessages = relationship('Message',
                           # foreign_keys="[Message.reciever_id]",
                           primaryjoin="and_(MbaUser.id==Message.reciever_id, Message.status==0)")


    available_invitation_codes = relationship('InvitationCode',
                                             primaryjoin="and_(MbaUser.id==InvitationCode.sender_id,"\
                                                         "InvitationCode.status==0)")



    city_id = Column(Integer, ForeignKey('city.id') ) # backref is defined in class City
    city_name = association_proxy('city'
            , 'name'
            , creator=City._find_or_create)


    def __init__(self, name, password=None,  confirm_token=None,
                 title=u"", email=None, groups=(), city_name='',
                 real_name='', birth_date=None, school=u"", school_year=0,
                 company=u"", industry=u"", special_skill=u"", interest=u"",
                 between=u"", introduction=u"", **kwargs):
        self.name = name
        if password is not None:
            password = get_principals().hash_password(password)
        self.password = password

        self.confirm_token = confirm_token
        self.title = title
        self.email = email
        self.groups = groups
        self.creation_date = datetime.now(tz=None)
        self.last_login_date = None

        if city_name:
            self.city_name = city_name
        else:
            # default city_name
            self.city_name = u'深圳'

        self.real_name = real_name
        self.birth_date = birth_date
        self.school = school
        self.school_year = school_year
        self.company = company
        self.industry = industry
        self.special_skill = special_skill
        self.between = between
        self.introduction = introduction

        super(MbaUser, self).__init__(**kwargs)



    @property
    def position_items(self):
        return [(rel, rel.position) for rel in self._positions]

    def __repr__(self):  # pragma: no cover
        return '<MbaUser %r>' % self.name

    @property
    def sex_info(self):
        if 0 == self.sex:
            return u"男"
        return u"女"

    def add_visit(self, u):
        v = None
        new_v = False
        try:
            v = DBSession.query(Visit).filter(Visit.user_id1==self.id, Visit.user_id2==u.id).one()
        except:
            new_v = True
        if not v:
            v = Visit(user_id1=self.id, user_id2=u.id)
        v.visit_date = datetime.now(tz=None)
        if new_v:
            DBSession.add(v)



    # @classproperty
    # def __mapper_args__(cls):
    #     return dict(
    #             order_by='mba_users.name',
    #             polymorphic_identity=camel_case_to_name(cls.__name__)
    #         )

    # id = Column('id', Integer, ForeignKey('mba_users.id'), primary_key=True)
    school = Column(String(100))
    school_year = Column(Integer())

    # real_name = Column(String(20))， real_name is put in superclass ,for global site, real name is needed
    birth_date = Column(Date())
    identify_type = Column(Integer())
    identify = Column(String(30))

    home_number = Column(String(20))
    # location = Column(String(20)) # location is duplicated with city_name in MbaUser
    salary = Column(Integer())
    work_years = Column(Integer())
    company_phone = Column(String(30))
    keyword = Column(String(100))
    job_status = Column(String(100))


    [AUTH_STATUS_UNAUTH, AUTH_STATUS_AUTHED, AUTH_STATUS_FAIL, AUTH_STATUS_REQ_FOR_AUTH ] = range(4)
    auth_info =  Column(Integer,default=AUTH_STATUS_UNAUTH) # 0, unauthed, 1 authed, 2 authfail, ( 3 request for auth?)
    auth_meetup =  Column(Integer,default=AUTH_STATUS_UNAUTH)
    auth_friend =  Column(Integer,default=AUTH_STATUS_UNAUTH) #
    auth_expert =  Column(Integer,default=AUTH_STATUS_UNAUTH) #

    @property
    def auth_honesty(self):
        return [self.auth_info, self.auth_meetup, self.auth_friend].count(self.AUTH_STATUS_AUTHED) >= 2



    resume = relationship('Resume', backref='user', uselist=False)
    #resumes = relationship('Resume', backref='user')



    def __repr__(self):  # pragma: no cover
        return '<Student %r>' % self.name

    @property
    def work_info(self):
        arrs = [u"小于一年", u"一到三年", u"三到五年", u"五年以上"]
        if self.work_years >= 0 and self.work_years < len(arrs):
            return arrs[self.work_years]
        return arrs[0]

    @property
    def birth_old(self):
        return abs(date.today().year - self.birth_date.year)+1


Student = MbaUser

friend_union = select([
                friend.c.user_a_id,
                friend.c.user_b_id
                ]).where(friend.c.status==1).union(
                        select([
                            friend.c.user_b_id,
                            friend.c.user_a_id,
                            ]).where(friend.c.status==1)
                ).alias()

MbaUser.all_friends = relationship('MbaUser',
                        secondary=friend_union,
                        primaryjoin=MbaUser.id==friend_union.c.user_a_id,
                        secondaryjoin=MbaUser.id==friend_union.c.user_b_id,
                        viewonly=True
)


my_requests = select([
                friend.c.user_a_id,
                friend.c.user_b_id
                ]).where(friend.c.status==0).alias()

MbaUser.my_requests = relationship('MbaUser',
                        secondary=my_requests,
                        primaryjoin=MbaUser.id==my_requests.c.user_a_id,
                        secondaryjoin=MbaUser.id==my_requests.c.user_b_id,
                        viewonly=True)


others_requests = select([
                friend.c.user_a_id,
                friend.c.user_b_id,
                ]).where(friend.c.status==0).alias()

MbaUser.others_requests = relationship('MbaUser',
                        secondary=others_requests,
                        primaryjoin=MbaUser.id==others_requests.c.user_b_id,
                        secondaryjoin=MbaUser.id==others_requests.c.user_a_id,
                        viewonly=True)




class Participate(Base):
    __tablename__ = 'participate'
    user_id = Column(Integer, ForeignKey('mba_users.id'), primary_key=True)
    act_id = Column(Integer, ForeignKey('acts.id'), primary_key=True)
    creation_date = Column(DateTime(), nullable=False, default=datetime.now)
    #用户参加活动之后可进行评分
    rating = Column(Integer())
    user = relationship("MbaUser", backref=backref("partin",
                                            cascade="all, delete-orphan") )
    meetup = relationship("Act")


class TeacherTag(Base):

    __tablename__ = 'teacher_tags'

    id = Column(Integer, primary_key=True)
    title = Column(Unicode(100), unique=True, nullable=False)

    def __repr__(self):
        return "<TeacherTag ('%s')>" % self.title

    @property
    def items(self):
        return [rel.item for rel in self.content_tags]

class TeacherTagToActs(Base):
    __tablename__ = 'teacher_tag_to_acts'
    #
    tag_id = Column(Integer, ForeignKey('teacher_tags.id'), primary_key=True)
    content_id = Column(Integer, ForeignKey('acts.id'), primary_key=True)
    teacher_tag = relation(TeacherTag, backref=backref('teacher_tags', cascade='all'))
    position = Column(Integer, nullable=False)
    title = association_proxy('teacher_tag', 'title')

    @classmethod
    def _tag_find_or_create(cls, title):
        with DBSession.no_autoflush:
            tag = DBSession.query(TeacherTag).filter_by(title=title).first()
        if tag is None:
            tag = TeacherTag(title=title)
        return cls(teacher_tag=tag)

# class ActStatus:
#     PUBLIC, DRAFT, PRIVATE, CANCEL, DELETED = 0, 1, 2, 3, 4
#     # public :  seen by anyone
#     # priveate: seen by admins
#     # draft: seen by self.
#     # cancel: meetup is canceled . 由于某些原因 管理员人为的取消活动
#     # deleted: meetup is deleted . 如果活动已经有人报名，将不能删除

# # 是否是活动首页推荐、全站首页推荐,全站首页推荐待考虑
# class HeadLine:
#     NOT_TOP, MEETUPS_TOP, SITE_TOP = 0, 1, 2

# 活动的类别        
class MeetupType(Base):
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=True)
    acts = relationship("Act", backref='meetup_types')

from kotti.views.edit.content import Image
#Image.acts = relationship("Act", backref('images'))

#人数限制、钱钱、地点、嘉宾
# Act means activity
class Act(Document):
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)
    __acl__ = SITE_ACL

    [STATUS_PUBLIC, STATUS_DRAFT, STATUS_PRIVATE, STATUS_CANCEL, STATUS_DELETED] = range(5)
    status = Column(Integer(), nullable=False, default=STATUS_PUBLIC)

    [PUTONBANNER_NO, PUTONBANNER_MEETUP, PUTONBANNER_HOME] = range(3)
    headline = Column(Integer, nullable=False, default=PUTONBANNER_NO)
    
    meetup_type = Column(Integer, ForeignKey('meetup_types.id'))    
    meetup_type_title = association_proxy('meetup_types', 'title' )





    #海报ID
    # poster_id =  Column(Integer, ForeignKey('images.id'))
    # poster = relationship('Image')
    # @property
    # def poster_img(self):
    #     # return  "/images/%s/image/" % (self.poster.name)
    #     return self.poster_img_url

    poster_img = Column(String(200)) # change 50 to 200 , 2014.10.29 by sunset


    
    # TODO Ignore the city ?
    city_id = Column(Integer, ForeignKey('city.id'))
    city_name = association_proxy('city'
            , 'name'
            , creator=City._find_or_create)


    # Meetup start time
    meetup_start_time = Column(DateTime(timezone=TZ_HK))
    # Meetup finish time
    meetup_finish_time = Column(DateTime(timezone=TZ_HK))
    enroll_finish_time = Column(DateTime(timezone=TZ_HK))
    enroll_start_time = Column(DateTime(timezone=TZ_HK))


    location = Column(UnicodeText())

    #经度
    latitude = Column(Float())
    longitude = Column(Float())
    zoomlevel = Column(Integer())


    _teacher_tags = relation(
        TeacherTagToActs,
        backref=backref('item'),
        order_by=[TeacherTagToActs.position],
        collection_class=ordering_list("position"),
        cascade='all, delete-orphan',
        )

    teachers = association_proxy(
        '_teacher_tags',
        'title',
        creator=TeacherTagToActs._tag_find_or_create,
        )

    limit_num = Column(Integer(), default=500)
    pay_count = Column(Integer(), default=0)
    #TODO for teacher selected

    type_info = Document.type_info.copy(
        name=u'Act',
        title=_(u'Act'),
        add_view=u'add_act',
        addable_to=[u'Act'],
        )
    
    _parts = relationship('Participate', backref='act')

    @property
    def parts(self):
        return [rel.user for rel in self._parts]
        
    _comments = relationship('Comment', backref='act')
    
    reviews = relationship('Review', backref='act')
    # @property
    # def comments(self):
        # return [i. for rel in self._comments]
    
class Review(Document):
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)    
    review_to_meetup_id = Column('review_to_meetup_id', Integer)
    type_info = Document.type_info.copy(
        name=u'Review',
        title=_(u'Review'),
        add_view=u'add_review',
        addable_to=[u'Review'],
        )    
    comments = relationship('Comment', backref='reivew')



class Infomation(Document):
    '''This Class stores the infomatino recommended by admins '''
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)

    [STATUS_PUBLIC, STATUS_DRAFT, STATUS_PRIVATE, STATUS_CANCEL, STATUS_DELETED] = range(5)
    status = Column(Integer(), nullable=False, default=STATUS_PUBLIC)



    type_info = Document.type_info.copy(
        name=u'Infomation',
        title=_(u'推荐信息'),
        add_view=u'add_info',
        addable_to=[u'Infomation'],
        )

    comments = relationship('Comment', backref='infomation')

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    
    TYPE_MEETUP = 0
    TYPE_MEETUP_REVIEW = 1
    TYPE_INFOMATION = 2
    
    # 评论类型，0=活动评论，1=活动回顾评论, 2=推荐信息评论
    type = Column(Integer, default=TYPE_MEETUP)
    # 评论关联的活动、活动回顾的ID
    document_id = Column(Integer, ForeignKey('documents.id'))
    
    user_id = Column(Integer, ForeignKey('mba_users.id'))
    content = Column(String(500),  nullable=True)
    
    
    user = relationship("MbaUser", backref='comment')
    
    post_date = Column(DateTime(), nullable=False, default=datetime.now)
    



# Tables about resume
# Education n -- 1 Resume 
class Education(Base):
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    school_name = Column(String(100), nullable=False)
    location = Column(String(100))
    start_date = Column(Date())
    finish_date = Column(Date())
    major = Column(String(30))
    degree = Column(Integer())
    abroad =  Column(Boolean)
    summary = Column(UnicodeText())

# Job n -- 1 Resume 
class Job(Base):
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    location = Column(String(200))
    industy = Column(String(100))
    industy_type = Column(Integer())
    industy_scale = Column(Integer())
    duty = Column(String(200))
    start_date = Column(Date())
    finish_date = Column(Date())
    description = Column(UnicodeText())
    is_current = Column(Boolean, default=False)

class Train(Base):
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    start_date = Column(DateTime())
    finish_date = Column(DateTime())
    location = Column(String(200))
    course = Column(String(100))
    certificate = Column(String(50))
    summary = Column(UnicodeText())

class ProjectInfo(Base):
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    start_date = Column(DateTime())
    finish_date = Column(DateTime())
    name = Column(String(200))
    tool = Column(String(200))
    hardware = Column(String(200))
    software = Column(String(200))
    description = Column(UnicodeText())
    duty = Column(UnicodeText)

class Language(Base):
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    lang_type = Column(String(20))
    grasp = Column(String(20))
    read_cap = Column(String(20))
    write_cap = Column(String(20))

# resume many to many skill
class ResumeSkill(Base):
    resume_id = Column(Integer, ForeignKey('resumes.id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('skills.id'), primary_key=True)
    skill = relationship('Skill', backref='resume_items')
    name = association_proxy('skill', 'name')

    @classmethod
    def _skill_find_or_create(cls, name):
        with DBSession.no_autoflush:
            skill = DBSession.query(Skill).filter_by(name=name).first()
        if skill is None:
            skill = Skill(name=name)
        return cls(skill=skill)

class Skill(Base):
    __table_args__ = (
        UniqueConstraint('name'),
        )
    id = Column(Integer, primary_key=True)
    name = Column(String(250))

    @property
    def resumes(self):
        return [rel.resume for rel in self.resume_items]

class Resume(Base):
    #id = Column(Integer, primary_key=True)
    #user_id = Column(Integer, ForeignKey('mba_users.id'))
    id = Column(Integer, ForeignKey('mba_users.id'), primary_key=True)
    title = Column(String(250))
    create_date = Column(DateTime(), default=datetime.utcnow)
    modify_date = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    _skills = relationship('ResumeSkill', backref='resume')
    skills = association_proxy(
        '_skills',
        'name',
        creator=ResumeSkill._skill_find_or_create,
        )

    # String like jobid1,jobid2,jobid3 5,6,3,1 
    job_order = Column(String(100), nullable=True)
    jobs = relationship('Job', cascade="save-update, merge, delete")
    projects = relationship('ProjectInfo', cascade="save-update, merge, delete")
    educations = relationship('Education', cascade="save-update, merge, delete")
    trains = relationship('Train', cascade="save-update, merge, delete")
    langs = relationship('Language', cascade="save-update, merge, delete")

    publicity = Column(Boolean, default=True)

    def order_jobs(self):
        jobs = self.jobs
        ids = dict([(obj.id,obj) for obj in jobs])
        rlts = []
        for s in self.job_order.split(','):
            id = int(s)
            if id in ids:
                rlts.append(ids[id])
        return (rlts+list(set(jobs).difference(set(rlts))))

def get_act_root(request=None):
    return DBSession.query(Document).filter_by(name="meetup").one()
    
def get_review_root(request=None):
    return DBSession.query(Document).filter_by(name="review").one()
    
def get_image_root(request=None):
    return DBSession.query(Document).filter_by(name="images").one()

def get_info_root(request=None):
    return DBSession.query(Document).filter_by(name="infomation").one()

class CompanyInfo(Base):
    id = Column('id', Integer, primary_key=True)
    name = Column(String(100))
    scope = Column(String(200))
    industry = Column(String(200))
    type_info = Column(String(200))
    location = Column(String(300))
    description = Column(UnicodeText())

#用户投给职位的简历
class PositionResume(Base):
    position_id = Column(Integer, ForeignKey('positions.id'), primary_key=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'), primary_key=True)
    create_date = Column(DateTime(), default=datetime.utcnow())
    #反馈状态
    status = Column(Integer())
    resume = relationship('Resume', backref='postition_items')
    user = association_proxy('resume', 'user')

#工作职位表 views/active.py
class Position(Document):
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)
    company_id = Column(Integer, ForeignKey('company_infos.id'))
    city_name = Column(String(100))
    degree = Column(String(100))
    experience = Column(String(100))
    salary = Column(Integer(), default=0)
    public_date = Column(Date(), default=datetime.now(tz=None).date())
    end_date = Column(Date(), default=datetime.now(tz=None).date())
    location = Column(UnicodeText())
    #猎头/公司
    hunting_type = Column(Integer(), default=0)

    [STATUS_PUBLIC, STATUS_DRAFT] = range(2)
    status = Column(Integer(), nullable=False, default=STATUS_DRAFT)

    resumes = relationship('PositionResume', backref='position')
    users = association_proxy('resumes', 'user')
    company = relationship('CompanyInfo', backref='postitions')
    company_name = association_proxy('company', 'name')
    industry = association_proxy('company', 'industry')
    create_date = Column(DateTime(), default=datetime.now(tz=None))

    type_info = Document.type_info.copy(
        name=u'Position',
        title=_(u'Position'),
        add_view=u'add_position',
        addable_to=[u'Position'],
        )

row2dict = lambda r: {c.name: getattr(r, c.name) for c in r.__table__.columns}


class Banner(Base):
    id = Column(Integer, primary_key=True)

    banner_position = Column(Integer, default=0) # 0：home banner, 1:meetup 2： Job， Currently, home banner is the only selection


    [TYPE_HOME, TYPE_MEETUP, TYPE_JOB ] = [0, 1 , 2]

    type = Column(Integer, default=TYPE_HOME)  # 0: home Banner, 1:Meetup Banner, 2: Job Banner

    title = Column(String(100))

    img_url = Column(String(100))

    link_url = Column(String(100))

    htmlcontent = Column(String(500), default=0)

    last_edit_date =  Column(Date(), default=datetime.now(tz=None).date())

    [VALID, INVALID ] = [1, 0]
    status = Column(Integer, default=VALID)  # 1: 生效， 0:失效


class ValidationSms(Base):
    '''注册、重置密码时发送的验证短信的表'''
    __tablename__ = "register_sms"

    [TYPE_REGISTER, TYPE_RESET_PASSWORD] = [0,1]


    id = Column(Integer, primary_key=True)
    phonenum = Column(String(20))
    # type = Column(Integer, default=TYPE_REGISTER) #类型，TYPE_REGISTER注册时，TYPE_RESET_PASSWORD:重置密码时
    validate_code  = Column(String(20)) # 注册时发送的验证码
    send_datetime = Column(DateTime(), default=datetime.now(tz=None) )
    ip = Column(String(50))






class InvitationCode(Base):
    '''注册邀请码表'''

    [AVAILABLE, USED, EXPIRED ] = [0, 1, -1] # # 0, unused, 1: used. -1: unvailable

    id = Column(Integer, primary_key=True)
    code = Column(String(10))

    sender_id = Column('sender_id', Integer, ForeignKey('mba_users.id'))
    sender = relationship("MbaUser", foreign_keys="[InvitationCode.sender_id]")
    receiver_id = Column('receiver_id', Integer, ForeignKey('mba_users.id'))
    receiver = relationship("MbaUser", foreign_keys="[InvitationCode.receiver_id]",
                                                backref=backref("invitation_code",
                                                        cascade="all, delete-orphan"))
    expiration = Column(DateTime() )
    status = Column(Integer, default=AVAILABLE)

class GlobalSiteSetting(Base):

    [TRUE, FALSE] = [1, 0]

    id = Column(Integer, primary_key=True)
    need_invitationcode = Column(Integer, default=True)



class Univs(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    pinyin = Column(String(250), nullable=False)
    pprev = Column(String(250), nullable=False)

