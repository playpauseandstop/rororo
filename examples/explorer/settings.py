import os

from rororo import GET, static


# Debug settings
DEBUG = True

# Explorer settings
ROOT_DIR = os.path.expanduser('~')
SHOW_HIDDEN_ITEMS = True

# List of available routes
ROUTES = ('',
    GET('/{path:path}', 'views.explorer', name='explorer',
        renderer='explorer.html'),
)
