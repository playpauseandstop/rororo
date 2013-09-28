from rororo.tests import TestCase
from routr.utils import import_string
from webtest import TestApp

from app import app


class TestWebTest(TestCase):

    def setUp(self):
        self.client = TestApp(app)

    def test_comments(self):
        self.client.get('/', status=200)
