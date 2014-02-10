import colander
from mock import Mock
import logging

from mba.testing import DummyRequest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

class TestTags:
    def test_empty(self, root):
        logger.info('test_empty hear')
        assert root.tags == []
