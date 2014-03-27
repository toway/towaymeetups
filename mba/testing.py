# -*- coding: utf-8 -*-

import os
from os.path import join, dirname
from unittest import TestCase
from pytest import mark

from pyramid import testing
from pyramid.events import NewResponse
from pyramid.security import ALL_PERMISSIONS
from zope.deprecation.deprecation import deprecate
import transaction


# re-enable deprecation warnings during test runs
# however, let the `ImportWarning` produced by Babel's
# `localedata.py` vs `localedata/` show up once...
from warnings import resetwarnings
from babel import localedata
import compiler
localedata, compiler    # make pyflakes happy... :p
resetwarnings()


# py.test markers (see http://pytest.org/latest/example/markers.html)
user = mark.user


BASE_URL = 'http://localhost:6543'


class Dummy(dict):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class DummyRequest(testing.DummyRequest):
    is_xhr = False
    POST = dict()
    user = None
    referrer = None

    def is_response(self, ob):
        return (hasattr(ob, 'app_iter') and hasattr(ob, 'headerlist') and
                hasattr(ob, 'status'))


def testing_db_url():
    return os.environ.get('KOTTI_TEST_DB_STRING', 'sqlite://')


def _populator():
    from kotti import DBSession
    from kotti.resources import Document
    from kotti.populate import populate

    populate()
    for doc in DBSession.query(Document)[1:]:
        DBSession.delete(doc)
    transaction.commit()


def tearDown():
    from kotti import events
    from kotti import security
    from kotti.message import _inject_mailer

    # These should arguable use the configurator, so they don't need
    # to be torn down separately:
    events.clear()
    security.reset()

    _inject_mailer[:] = []
    transaction.abort()
    testing.tearDown()


def _initTestingDB():
    from sqlalchemy import create_engine
    from kotti import get_settings
    from kotti.resources import initialize_sql

    database_url = testing_db_url()
    get_settings()['sqlalchemy.url'] = database_url
    session = initialize_sql(create_engine(database_url), drop_all=True)
    return session


def setUp(init_db=True, **kwargs):
    #_turn_warnings_into_errors()

    from kotti import _resolve_dotted
    from mba import default_settings as conf_defaults
    tearDown()
    settings = conf_defaults.copy()
    settings['kotti.secret'] = 'secret'
    settings['kotti.secret2'] = 'secret2'
    settings['kotti.populators'] = 'mba.testing._populator'
    settings.update(kwargs.get('settings', {}))
    _resolve_dotted(settings)
    kwargs['settings'] = settings
    config = testing.setUp(**kwargs)
    config.add_default_renderers()

    if init_db:
        _initTestingDB()

    transaction.begin()
    return config


class UnitTestBase(TestCase):
    def setUp(self, **kwargs):
        self.config = setUp(**kwargs)

    def tearDown(self):
        tearDown()


#TODO how to implement auto testing ? so we can test it without create html pages
