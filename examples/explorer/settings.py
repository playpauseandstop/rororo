import os
import sys

import six

from rororo import GET, static


DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

# Debug settings
DEBUG = True
USE_WDB = not six.PY3 and not sys.version_info[:2] == (2, 7)

# Explorer settings
ROOT_DIR = os.path.expanduser('~')
SHOW_HIDDEN_ITEMS = True

# List of available routes
ROUTES = (
    static('favicon.ico', rel('static'), path='favicon.ico'),
    GET('/{path:path}', 'views.explorer', name='explorer',
        renderer='explorer.html'),
)

# Time zone settings
TIME_ZONE = 'UTC'
