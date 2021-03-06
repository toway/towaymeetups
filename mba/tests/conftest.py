# non-public test fixtures

from pytest import fixture
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@fixture
def app(db_session):
    from webtest import TestApp
    from mba.tests import setup_app
    logger.info('begin test hear')
    return TestApp(setup_app())


@fixture
def extra_principals(db_session):
    from kotti.security import get_principals
    P = get_principals()
    P[u'bob'] = dict(name=u'bob', title=u"Bob")
    P[u'frank'] = dict(name=u'frank', title=u"Frank")
    P[u'group:bobsgroup'] = dict(name=u'group:bobsgroup', title=u"Bob's Group")
    P[u'group:franksgroup'] = dict(name=u'group:franksgroup',
        title=u"Frank's Group")
