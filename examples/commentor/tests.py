from rororo import compat
from webtest import TestApp

from app import app, redis
from views import add_comment


TEST_AUTHOR = 'Test Author'
TEST_TEXT = 'Test Text'


class TestViews(compat.TestCase):

    def setUp(self):
        app.settings.REDIS_COMMENT_KEY_PATTERN = 'test:{0}'.format(
            app.settings.REDIS_COMMENT_KEY_PATTERN
        )
        app.settings.REDIS_COMMENTS_KEY = 'test:{0}'.format(
            app.settings.REDIS_COMMENTS_KEY
        )

    def tearDown(self):
        pattern = app.settings.REDIS_COMMENT_KEY_PATTERN
        map(redis.delete, redis.keys(pattern.format(uuid='*')))
        redis.delete(app.settings.REDIS_COMMENTS_KEY)

    def test_add_comment(self):
        comments_key = app.settings.REDIS_COMMENTS_KEY
        self.assertEqual(redis.llen(comments_key), 0)

        self.assertTrue(add_comment(TEST_AUTHOR, TEST_TEXT))
        self.assertEqual(redis.llen(comments_key), 1)


class TestWebTest(compat.TestCase):

    def setUp(self):
        self.client = TestApp(app)

    def test_comments(self):
        self.client.get('/', status=200)
