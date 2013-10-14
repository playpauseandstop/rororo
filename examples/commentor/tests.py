from rororo import compat
from routr.utils import import_string
from webtest import TestApp

from app import app


class TestWebTest(compat.TestCase):

    def setUp(self):
        self.client = TestApp(app)

    def test_comments(self):
        self.client.get('/', status=200)
