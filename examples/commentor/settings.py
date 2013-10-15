from rororo import compat
from rororo.routes import GET, POST
from rororo.schema import form
from rororo.views import blank


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
    GET('/', blank, name='index', renderer='index.html'),
    POST('/api/comment/add',
         form(author=compat.text_type, text=compat.text_type),
         'add_comment',
         renderer='json'),
    GET('/api/comments', 'get_comments', name='get_comments', renderer='json'),
)
ROUTES_VIEW_PREFIX = 'views'

# Other settings
COMMENTS_PER_PAGE = 30
DATETIME_FORMAT = '%c'
JINJA_FILTERS = {'format': format}
