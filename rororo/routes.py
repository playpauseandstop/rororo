"""
=============
rororo.routes
=============

Provide shortcuts for routes functions and helpers.

"""

from .utils import inject_module


inject_module('routr',
              locals(),
              include_attr=('DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH',
                            'POST', 'PUT', 'TRACE', 'include', 'plug',
                            'route'))
