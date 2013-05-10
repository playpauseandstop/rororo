"""
=============
rororo.static
=============

Extended static view which has support of package static directories.

"""

import os

from routr import GET
from routr.static import _ForceResponse
from webob.static import FileApp

from .schema import defaults


def make_static_view(dirnames):
    """
    Make actual static view.
    """
    def static_view(request, path):
        """
        Try to find requested ``path`` in ``dirnames`` sequence, if possible
        return file content to browser, else raise 404 error.
        """
        sequence = (dirnames
                    if isinstance(dirnames, (list, tuple))
                    else (dirnames, ))

        for dirname in sequence:
            filename = os.path.join(dirname, path)

            if os.path.isfile(filename):
                return _ForceResponse(FileApp(filename)(request))

        # If no static file found use app static dir to point about error,
        # not package static dir
        filename = os.path.join(dirnames[0], path)
        return _ForceResponse(FileApp(filename)(request))

    static_view.static_view = True
    return static_view


def static(prefix, dirnames=None, **kwargs):
    """
    Route for serving static assets.

    In comparison with default ``routr.static:static`` function ``static`` has
    support of multiple static directories.
    """
    kwargs['static_view'] = True
    path = kwargs.pop('path', None)

    if path:
        return GET(prefix,
                   defaults(path=path),
                   make_static_view(dirnames),
                   **kwargs)

    return GET('{0}/{{path:path}}'.format(prefix.rstrip('/')),
               make_static_view(dirnames),
               **kwargs)
