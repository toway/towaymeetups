import os
from UserDict import DictMixin
from fnmatch import fnmatch
from datetime import datetime

from pyramid.threadlocal import get_current_registry
from pyramid.traversal import resource_path
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import UniqueConstraint
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
from kotti.security import view_permitted
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


#This is a base class for all users
class MbaUser(Base):

    __mapper_args__ = dict(
        order_by='mba_users.name',
        polymorphic_on='type',
        polymorphic_identity='mba_users',
        #with_polymorphic='*',
        )

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), unique=True)
    password = Column(Unicode(100))
    active = Column(Boolean)
    confirm_token = Column(Unicode(100))
    title = Column(Unicode(100), nullable=False)
    email = Column(Unicode(100), unique=True)
    groups = Column(JsonType(), nullable=False)
    creation_date = Column(DateTime(), nullable=False)
    last_login_date = Column(DateTime())

    #TODO how to set a picture?

    #The real user type(Student, Teacher, Professor or Company?
    #obj_type = Column(Integer(), nullable=False)
    #ref to Kotti.Node
    type = Column(String(50), nullable=False)

    def __init__(self, name, password=None, active=True, confirm_token=None,
                 title=u"", email=None, groups=(), **kwargs):
        self.name = name
        if password is not None:
            password = get_principals().hash_password(password)
        self.password = password
        self.active = active
        self.confirm_token = confirm_token
        self.title = title
        self.email = email
        self.groups = groups
        self.creation_date = datetime.now()
        self.last_login_date = None
        super(MbaUser, self).__init__(**kwargs)

    def __repr__(self):  # pragma: no cover
        return '<MbaUser %r>' % self.name
    '''
    def real_user(self):
        pass
    '''


class Participate(Base):
    __tablename__ = 'participate'
    user_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    act_id = Column(Integer, ForeignKey('acts.id'), primary_key=True)
    creation_date = Column(DateTime(), nullable=False, default=datetime.now)
    #acts = relation(Act, backref=backref('part_users', cascade='all'))
    user = relationship("Student", backref='partin')


class ActStatus:
    DRAFT, PUBLIC, FINISH, CANCEL = 0, 1, 2, 3


# Act means activity
class Act(Document):
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)
    status = Column(Integer(), nullable=False)

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


class Student(MbaUser):

    @classproperty
    def __mapper_args__(cls):
        return dict(
                order_by='mba_users.name',
                polymorphic_identity=camel_case_to_name(cls.__name__)
            )

    id = Column('id', Integer, ForeignKey('mba_users.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, name,  **kwargs):
        super(Student, self).__init__(name, **kwargs)


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
    a = Act(**_TEST_ATTRS)
    p = Participate()
    p.user = Student(name=u'test')
    a._parts.append(p)
    DBSession.add(a)
    DBSession.flush()
    act = DBSession.query(Act).first()
    print 'query Act', act.id
    print 'Act.parts', act.parts


def populate():
    print 'Just test in mba.resources: '
    #test_document()
    #test_act()
    #test_act2()
