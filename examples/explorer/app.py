"""
===
app
===

Main Explorer application and custom validate management command.

"""

import os

from rororo import create_app, manage

import settings


# Custom management command
def validate():
    """
    Validate settings values.
    """
    if not os.path.isdir(settings.ROOT_DIR):
        print >> sys.stderr, 'Root directory not found at {!r}'.\
                             format(settings.ROOT_DIR)
        return False

    print('All OK!')


# Create rororo-compatible app
app = create_app(settings)


# Run rororo manager
if __name__ == '__main__':
    manage(app, validate)
