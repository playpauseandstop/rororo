import os
import sys

import six

from rororo import GET


# Debug settings
DEBUG = True
USE_WDB = not six.PY3 and not sys.version_info[:2] == (2, 7)

# Explorer settings
ROOT_DIR = os.path.expanduser('~')
SHOW_HIDDEN_ITEMS = True

# List of available routes
ROUTES = ('',
    GET('/{path:path}', 'views.explorer', name='explorer',
        renderer='explorer.html'),
)
