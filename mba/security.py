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
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.util import classproperty
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
from kotti.util import camel_case_to_name
from kotti.security import Principals, get_principals

from mba.resources import MbaUser, Student


'''
class Teacher(MbaUser):
    __tablename__ = 'teacher'
    __mapper_args__ = dict(
        order_by='teacher.name',
        )
    id = Column('id', Integer, ForeignKey('mbauser.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, **kwargs):
        super(Teacher, self).__init__(**kwargs)


class Professor(MbaUser):
    __tablename__ = 'professor'
    __mapper_args__ = dict(
        order_by='professor.name',
        )
    id = Column('id', Integer, ForeignKey('mbauser.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, **kwargs):
        super(Professor, self).__init__(**kwargs)


# Implement in the next version
class Company(MbaUser):
    __tablename__ = 'company'
    __mapper_args__ = dict(
        order_by='company.name',
        )
    id = Column('id', Integer, ForeignKey('mbauser.id'), primary_key=True)
    #TODO for the other column

    def __init__(self, **kwargs):
        super(Company, self).__init__(**kwargs)
'''

class MbaPrincipals(Principals):
    #factory = MbaUser
    factory = Student


def principals_factory():
    return MbaPrincipals()
