import io
import sys

from rororo import compat
from rororo.exceptions import HTTPNotFound
from rororo.manager import manage
from webtest import TestApp

from app import app, manager, settings
from views import explorer


class TestCustomCommands(compat.TestCase):

    def tearDown(self):
        sys.argv = self.old_argv
        sys.stdout = self.old_stdout

    def test_hello(self):
        self.old_stdout = sys.stdout
        self.old_argv = sys.argv

        sys.stdout = io.StringIO() if compat.IS_PY3 else io.BytesIO()
        sys.argv = [sys.argv[0], '--help']

        self.assertRaises(SystemExit, manager, app)

        sys.stdout.seek(0)
        content = sys.stdout.read()
        self.assertIn('hello', content)
        self.assertIn('validate', content)

        sys.stdout = io.StringIO() if compat.IS_PY3 else io.BytesIO()

        self.assertRaises(SystemExit, manage, app)

        sys.stdout.seek(0)
        content = sys.stdout.read()
        self.assertNotIn('hello', content)
        self.assertNotIn('validate', content)


class TestViews(compat.TestCase):

    def test_does_not_exist(self):
        self.assertRaises(HTTPNotFound, explorer, '/does_not_exist')

    def test_exists(self):
        listing = explorer('')
        self.assertTrue(listing)


class TestWebTest(compat.TestCase):

    def setUp(self):
        self.client = TestApp(app)

    def test_does_not_exist(self):
        self.client.get('/does_not_exist.exe', status=404)

    def test_favicon(self):
        favicon = open(settings.rel('static', 'favicon.ico'), 'rb').read()
        response = self.client.get('/favicon.ico', status=200)
        self.assertEqual(response.body, favicon)

    def test_index(self):
        response = self.client.get('/', status=200)
        self.assertIn('<title>File Explorer</title>', response.ubody)
