"""
=====
views
=====

Explorer view.

If path is a directory - get list with all child directories and files, of path
is a file - get file content, if path does not exist - show 404 error page.

"""

import operator
import os

from urllib2 import quote

from rororo.exceptions import HTTPNotFound

import settings


def explorer(path):
    """
    First validate path, it shouldn't start with "..".

    Then if ``path`` is a directory - return sorted list of files and
    directories, if ``path`` is a file - return response with file content, but
    if ``path`` not exists - raise ``HTTPNotFound`` exception.
    """
    error = u'Does not exist: {}'
    raw_path = path.decode('utf-8') if isinstance(path, str) else path

    if path.startswith('..') or path.startswith(os.sep):
        raise HTTPNotFound(error.format(path))

    path = os.path.join(settings.ROOT_DIR, os.sep.join(path.split('/')))
    path = path.decode('utf-8') if isinstance(path, str) else path

    if os.path.isdir(path):
        children = []
        items = os.listdir(path)

        for item in items:
            if settings.SHOW_HIDDEN_ITEMS and item.startswith('.'):
                continue

            item_path = os.path.join(path, item)
            item_url = u'/'.join((raw_path, item)) if raw_path else item

            child = {
                'name': item,
                'path': item_path,
                'stat': os.stat(item_path),
                'type': 'directory' if os.path.isdir(item_path) else 'file',
                'url': quote(item_url.encode('utf-8')),
            }
            children.append(child)

        children = sorted(children, key=operator.itemgetter('type'))
        context = {
            'children': children,
            'path': path,
            'raw_path': raw_path,
            'type': 'directory',
        }

        if raw_path:
            parts = raw_path.split(u'/')
            context.update(parent=quote(u'/'.join(parts[:-1])))

        return context
    elif os.path.isfile(path):
        with open(path, 'r') as handler:
            content = handler.read()
        return {'content': content, 'path': path, 'type': 'file'}
    else:
        raise HTTPNotFound(error.format(raw_path))
