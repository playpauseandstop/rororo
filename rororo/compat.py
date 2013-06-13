"""
=============
rororo.compat
=============

Why we need six, if we can provide compat functions and modules which working
on both of Python 2 and 3 by ourself? :)

"""

import sys

from functools import partial


# Are we working on Python 3 or not?
IS_PY3 = sys.version_info[0] == 3

# Python 3 hasn't func_name attribute, but Python 2 has
func_name = lambda func: func.__name__ if IS_PY3 else func.func_name

# Integer, string and text type(s)
integer_types = (int, ) if IS_PY3 else (int, long)
string_types = (str, bytes) if IS_PY3 else (basestring, )
text_type = str if IS_PY3 else unicode

# Python 3 hasn't iteritems, but Python 2 has
iteritems = lambda data: data.items() if IS_PY3 else data.iteritems()

# Little trick to do Unicode on Python 2 and 3
u = str if IS_PY3 else partial(unicode, encoding='utf-8')
