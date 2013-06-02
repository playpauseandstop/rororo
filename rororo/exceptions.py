"""
=================
rororo.exceptions
=================

All exceptions from WebOb, routr and rororo in one place.

"""

from string import Template

from routr import exc as routr_exceptions
from webob import exc as webob_exceptions


class HTTPServerError(webob_exceptions.HTTPServerError):
    """
    Modify server errors to print tracebacks in debug mode.
    """
    body_template_obj = Template("""${explanation}<br /><br />
<pre>${detail}</pre>
${html_comment}
""")


class ImproperlyConfigured(Exception):
    """
    Class for improperly configured errors.
    """


class NoRendererFound(ValueError):
    """
    Prettify message for "No renderer found" exception.
    """
    def __init__(self, renderer):
        message = 'Renderer {0!r} does not exist.'.format(renderer)
        super(NoRendererFound, self).__init__(message)


class ValidationError(Exception):
    """
    Class for validation errors.

    This is very basic class, no specific outputs or other things which
    happened somewhere else. Just put an error message and then print it in
    template for example.
    """


def inject(module):
    """
    Inject all exceptions from module to global namespace.
    """
    for attr in dir(module):
        if attr.startswith('_') or attr in globals():
            continue

        value = getattr(module, attr)

        if isinstance(value, type) and issubclass(value, Exception):
            globals()[value.__name__] = value


inject(routr_exceptions)
inject(webob_exceptions)
