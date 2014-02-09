from __future__ import with_statement
from contextlib import contextmanager
from datetime import datetime
from UserDict import DictMixin

import bcrypt
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm.exc import NoResultFound
from pyramid.location import lineage
from pyramid.security import authenticated_userid
from pyramid.security import has_permission as base_has_permission
from pyramid.security import view_execution_permitted

from kotti import get_settings
from kotti import DBSession
from kotti import Base
from kotti.sqla import JsonType
from kotti.util import _
from kotti.util import request_cache
from kotti.util import DontCache
from kotti.security import Principals, get_principals


class UserType:
    USER_BASE, STUDENT, TEACHER, PROFESSOR, COMPANY = 0, 1, 2, 3, 4


#TODO extent Principal or create new one with ForeignKey('Principal.id') ?
'''
class MbaPrincipal(Principal):

    __tablename__ = 'mbausers'
    __mapper_args__ = dict(
        order_by='principals.name',
        )
    id = Column('id', Integer, ForeignKey('principals.id'), primary_key=True)
    class_number = Column(Unicode(100), nullable=False)

    def __init__(self, name, password=None, active=True, confirm_token=None,
                 title=u"", email=None, groups=(), class_number=u""):
        super(MbaPrincipal, self).__init__(name, password, active, confirm_token,
                 title, email, groups)
        self.class_number = class_number
'''


#This is a base class for all users
class MbaUser(Base):
    __tablename__ = 'mbauser'
    __mapper_args__ = dict(
        order_by='mbauser.name',
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
    obj_type = Column(Integer(), nullable=False)

    def __init__(self, name, password=None, active=True, confirm_token=None,
                 title=u"", email=None, groups=(), obj_type=UserType.USER_BASE):
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
        self.obj_type = obj_type

    def __repr__(self):  # pragma: no cover
        return '<MbaUser %r>' % self.name
    '''
    def real_user(self):
        pass
    '''


class Student(MbaUser):
    __tablename__ = 'student'
    __mapper_args__ = dict(
        order_by='student.name',
        )
    id = Column('id', Integer, ForeignKey('mbauser.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, name, password=None, active=True, confirm_token=None,
                 title=u"", email=None, groups=(), obj_type=UserType.USER_BASE):
        super(Student, self).__init__(name, password, active, confirm_token,
                 title, email, groups, UserType.TEACHER)


class Teacher(MbaUser):
    __tablename__ = 'teacher'
    __mapper_args__ = dict(
        order_by='teacher.name',
        )
    id = Column('id', Integer, ForeignKey('mbauser.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, name, password=None, active=True, confirm_token=None,
                 title=u"", email=None, groups=(), obj_type=UserType.USER_BASE):
        super(Teacher, self).__init__(name, password, active, confirm_token,
                 title, email, groups, UserType.TEACHER)


class Professor(MbaUser):
    __tablename__ = 'professor'
    __mapper_args__ = dict(
        order_by='professor.name',
        )
    id = Column('id', Integer, ForeignKey('mbauser.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, name, password=None, active=True, confirm_token=None,
                 title=u"", email=None, groups=(), obj_type=UserType.USER_BASE):
        super(Professor, self).__init__(name, password, active, confirm_token,
                 title, email, groups, UserType.PROFESSOR)


# Implement in the next version
class Company(MbaUser):
    __tablename__ = 'company'
    __mapper_args__ = dict(
        order_by='company.name',
        )
    id = Column('id', Integer, ForeignKey('mbauser.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, name, password=None, active=True, confirm_token=None,
                 title=u"", email=None, groups=(), obj_type=UserType.USER_BASE):
        super(Company, self).__init__(name, password, active, confirm_token,
                 title, email, groups, UserType.COMPANY)


class MbaPrincipals(Principals):
    factory = MbaUser


def principals_factory():
    return MbaPrincipals()
