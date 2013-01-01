"""
==============
rororo.manager
==============

Support of custom management commands for rororo framework.

"""

import sys

from argparse import ArgumentParser
from wsgiref.simple_server import make_server


DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8000


def manage(app, *commands):
    pass


def run(app, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """
    Run simple WSGI server
    """
    server = make_server(host, int(port), app)

    try:
        print('Starting server at http://{}:{}/'.format(host, port))
        server.serve_forever()
    except KeyboardInterrupt:
        print
