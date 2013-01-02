"""
==============
rororo.manager
==============

Support of custom management commands for rororo framework.

"""

import copy
import inspect
import operator
import subprocess
import sys
import types

from argparse import ArgumentParser

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from wsgiref.simple_server import make_server

import server_reloader


DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8000


def manage(app, *commands):
    """
    Find all possible management commands from functions in current module and
    add them as sub-commands to main argument parser.

    You also could to add more custom management commands as positional
    arguments while calling this function.

    .. note:: Each management function should get ``app`` as first positional
       arg. All other arguments should be optional.
    """
    # Initialize parser
    parser = ArgumentParser(description='rororo management commands.')
    subparsers = parser.add_subparsers(
        description='List of available commands.',
        title='commands'
    )

    # Find all available management commands and add they as parser sub-command
    data = copy.copy(globals().items())
    ignore = ('manage', )

    for func in commands:
        data.append((func.func_name, func))

    data = sorted(data, key=operator.itemgetter(0))

    for key, value in data:
        # Only functions from current module would be available as sub-commands
        if key.startswith('_') or key in ignore or \
           not isinstance(value, types.FunctionType) or \
           (value.__module__ != __name__ and not value in commands):
            continue

        # Add sub-command to main parser
        kwargs = {}
        if value.__doc__:
            kwargs['help'] = value.__doc__.replace('\n', ' ').strip()
        subparser = subparsers.add_parser(key, **kwargs)

        # Read function args spec to add necessary arguments to subcommand
        spec = inspect.getargspec(value)

        args, defaults = spec.args or (), spec.defaults or ()
        defaults_start = len(args) - len(defaults)

        for i, arg in enumerate(args):
            if arg == 'app':
                continue

            kwargs = {}

            if i >= defaults_start:
                default = kwargs['default'] = defaults[i - defaults_start]

                if isinstance(default, bool):
                    kwargs['action'] = \
                        'store_true' if not default else 'store_false'

                    if default:
                        arg = 'no-{}'.format(arg)

                kwargs['help'] = 'By default: {}'.format(default)

            arg = arg.replace('_', '-')
            subparser.add_argument('--{}'.format(arg), **kwargs)

        # Run function
        subparser.set_defaults(func=value)

    # Parse arguments from command line
    no_args = len(sys.argv) == 1

    if no_args:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = StringIO(), StringIO()

    try:
        args = parser.parse_args(sys.argv[1:])
    except SystemExit as err:
        if err.code:
            if no_args:
                sys.stdout, sys.stderr = old_stdout, old_stderr
                parser.print_help()
            sys.exit(err.code)
        raise err

    # Run necessary function if everything ok
    kwargs = dict([
        (key.replace('-', '_').replace('no_', ''), value) \
        for key, value in args._get_kwargs() \
        if key != 'func'
    ])
    return args.func(app, **kwargs)


def clean_pyc(app):
    """
    Remove all *.pyc files which contains in APP_DIR.
    """
    cmd = 'find "{}" -name "*.pyc" -exec rm -rf {{}} \;'.\
          format(app.settings.APP_DIR)
    subprocess.call(cmd, shell=True)


def print_settings(app):
    """
    Print application settings as key => value lines.
    """
    for attr in dir(app.settings):
        if attr.startswith('_'):
            continue
        print('{} = {!r}'.format(attr, getattr(app.settings, attr)))


def run(app, host=DEFAULT_HOST, port=DEFAULT_PORT, autoreload=True):
    """
    Run Python's standard simple WSGI server with ability to autoreload on file
    changes.
    """
    def before_reload():
        """
        Show message before server reloaded.
        """
        print('Reloading server...\n')

    def run_server():
        """
        Run simple WSGI server.
        """
        server = make_server(host, int(port), app)

        try:
            print('Starting server at http://{}:{}/'.format(host, port))
            server.serve_forever()
        except KeyboardInterrupt:
            print

    if autoreload:
        server_reloader.main(run_server, before_reload=before_reload)
    else:
        run_server()


def test(app, tests=None):
    """
    Run all or only specified tests from APP_DIR.
    """
