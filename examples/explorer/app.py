"""
===
app
===

Main Explorer application and custom validate management command.

"""

from __future__ import print_function

import os
import sys

from rororo.app import create_app
from rororo.manager import manage

import commands
import settings


# Custom management command
def validate(app, something):
    """
    Validate settings values.
    """
    if not os.path.isdir(settings.ROOT_DIR):
        print('Root directory not found at {0!r}'.format(settings.ROOT_DIR),
              file=sys.stderr)
        sys.exit(1)

    print('All OK!')


# Create rororo-compatible app and manager
app = create_app(settings)
manager = lambda app: manage(app, commands, validate)


# Run rororo manage if necessary
if __name__ == '__main__':
    manager(app)
