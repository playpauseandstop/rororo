from rororo.routes import GET, POST


# Debug settings
DEBUG = True

# PEP8 settings
USE_PEP8 = True
PEP8_CLASS = 'flake8.engine.get_style_guide'

# Redis settings
REDIS_URL = 'redis://127.0.0.1:6379/0'
REDIS_COMMENT_KEY_PATTERN = 'commentor:{uuid}'
REDIS_COMMENTS_KEY = 'commentor:comments'

# Routes settings
ROUTES = (
    GET('/', 'comments', name='comments', renderer='comments.html'),
    POST('/add', 'add_comment', renderer='add_comment.html'),
)
ROUTES_VIEW_PREFIX = 'views'

# Other settings
COMMENTS_PER_PAGE = 30
DATETIME_FORMAT = '%c'
JINJA_FILTERS = {'format': format}
