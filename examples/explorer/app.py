"""
===
app
===

Main Explorer application and custom validate management command.

"""

from __future__ import print_function

import os
import sys

from rororo import create_app, manage
from rororo.utils import get_commands

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


# Create rororo-compatible app
app = create_app(settings)

# Define rororo manager
manager = lambda app: manage(app, validate, *get_commands(commands))


# Run rororo manage if necessary
if __name__ == '__main__':
    manager(app)
