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
from kotti.security import Principal, Principals

#TODO extent Principal or create new one with ForeignKey('Principal.id') ?
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

class MbaPrincipals(Principals):
    factory = MbaPrincipal

def principals_factory():
    return MbaPrincipals()

