import os
from UserDict import DictMixin
from fnmatch import fnmatch

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
from sqlalchemy.orm import relation
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
from kotti.sqla import ACLType
from kotti.sqla import JsonType
from kotti.sqla import MutationList
from kotti.sqla import NestedMutationDict
from kotti.util import ViewLink
#from kotti.util import _
from kotti.util import camel_case_to_name
from kotti.util import get_paste_items
from kotti.resources import Document

from mba import _


class ActivityStatus:
    DRAFT, PUBLIC, FINISH, CANCEL = 0, 1, 2, 3


# Extent from document ?
# How to make a test?
class Activity(Document):
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)
    status = Column(Integer(), nullable=False)

    type_info = Document.type_info.copy(
        name=u'Activity',
        title=_(u'Activity'),
        add_view=u'add_activity',
        addable_to=[u'Activity'],
        )

'''
# For who participate what activity
# many to many relationship
# refer to many relationship of (tag <--> content)
participate = Table(
    'participate', Base.metadata,
    Column('mbauser_id', Integer, ForeignKey('mbauser.id')),
    #Column('')

class Participate(Base):
    id
'''
