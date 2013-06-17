"""
==============
rororo.manager
==============

Support of custom management commands for rororo framework.

"""

from __future__ import print_function

import copy
import inspect
import operator
import subprocess
import sys
import types

from argparse import ArgumentParser
from wsgiref.simple_server import make_server

import server_reloader

from routr.utils import import_string

from . import compat
from .utils import get_commands


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
    commands = get_commands(commands)
    data = list(copy.copy(globals()).items())
    ignore = ('manage', )

    for func in commands:
        data.append((compat.func_name(func), func))

    data = sorted(data, key=operator.itemgetter(0))

    for key, value in data:
        # Only functions from current module would be available as sub-commands
        if (
            key.startswith('_') or key in ignore or
            not isinstance(value, types.FunctionType) or
            (value.__module__ != __name__ and not value in commands)
        ):
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
            if arg == 'app' or arg.startswith('_'):
                continue

            kwargs = {}

            if i >= defaults_start:
                default = kwargs['default'] = defaults[i - defaults_start]

                if isinstance(default, bool):
                    kwargs['action'] = \
                        'store_true' if not default else 'store_false'

                    if default:
                        arg = 'no-{0}'.format(arg)

                kwargs['help'] = 'By default: {0}'.format(not default)

            arg = arg.replace('_', '-')
            subparser.add_argument('--{0}'.format(arg), **kwargs)

        # Run function
        subparser.set_defaults(func=value)

    # If no arguments, just show help and exit
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # Parse arguments from command line
    args = parser.parse_args(sys.argv[1:])

    # Run necessary function if everything ok
    kwargs = dict([
        (key.replace('-', '_').replace('no_', ''), value)
        for key, value in args._get_kwargs()
        if key != 'func'
    ])
    return args.func(app, **kwargs)


def clean_pyc(app):
    """
    Remove all *.pyc files which contains in APP_DIR.
    """
    cmd = 'find "{0}" -name "*.pyc" -exec rm -rf {{}} \;'.\
          format(app.settings.APP_DIR)
    subprocess.call(cmd, shell=True)


def pep8(app, _return_report=True):
    """
    Run PEP8 for all Python files in app directory and all available package
    directories.
    """
    # Nothing to do if PEP8 support disabled in settings
    if not app.settings.USE_PEP8:
        print('PEP8 checks disabled for current app. To enable define '
              '"USE_PEP8 = True" if app settings.')
        return False

    # Import PEP8 style guide
    guide_klass = import_string('pep8.StyleGuide')

    # Configure PEP8 style guide
    options = copy.deepcopy(app.settings.PEP8_OPTIONS)
    options['paths'] = [app.settings.APP_DIR] + app.settings._PACKAGE_DIRS

    # Initialize style guide and run files check
    guide = guide_klass(**options)
    report = guide.check_files()

    # Return report without any printing to stdout
    if _return_report:
        return report

    # If necessary - print statistics
    if guide.options.statistics:
        report.print_statistics()

    # If errors happened - show its number or just exit from function
    if report.total_errors:
        if guide.options.count:
            print(report.total_errors, file=sys.stderr)
        return False

    return True


def print_settings(app):
    """
    Print application settings as "key=value" lines.
    """
    for attr in dir(app.settings):
        if attr.startswith('_'):
            continue
        print('{0}={1!r}'.format(attr, getattr(app.settings, attr)))
    return True


def runserver(app, host=DEFAULT_HOST, port=DEFAULT_PORT, autoreload=True):
    """
    Run Python's standard simple WSGI server with ability to autoreload on file
    changes.
    """
    def before_exit():
        """
        Show message before exit by KeyboardInterrupt.
        """
        print('\nOK! OK! Exiting...')

    def before_reload():
        """
        Show message before server reloaded.
        """
        print('Reloading server...\n')

    def run_server():
        """
        Run simple WSGI server.

        Server should be with or without WDB web debugger and run PEP8
        checkings before each run.
        """
        if app.settings.USE_PEP8:
            report = pep8(app, True)

            if report.total_errors:
                print(
                    '\nPEP8 check resulted {0} error(s). Please, fix errors '
                    'before run development server or disable PEP8 check ups '
                    'in app settings.'.format(report.total_errors),
                    file=sys.stderr
                )
                sys.exit(1)

        wdb_app = None

        if app.settings.USE_WDB:
            wdb_klass = import_string('wdb:Wdb')
            wdb_app = wdb_klass(app, **app.settings.WDB_OPTIONS)

        server = make_server(host, int(port), wdb_app or app)

        print('Starting server at http://{0}:{1}/'.format(host, port))
        server.serve_forever()

    if autoreload:
        server_reloader.main(run_server,
                             before_exit=before_exit,
                             before_reload=before_reload)
    else:
        try:
            run_server()
        except KeyboardInterrupt:
            before_exit()

    return False


def test(app, tests=None):
    """
    Run all or only specified tests from APP_DIR.
    """
