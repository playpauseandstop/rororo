"""
=================
rororo.exceptions
=================

All exceptions from WebOb, routr and rororo in one place.

"""

from string import Template

from routr import exc as routr_exceptions
from schemify import ValidationError as BaseValidationError
from webob import exc as webob_exceptions

from .utils import inject_exceptions


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


class ValidationError(BaseValidationError):
    """
    Class for validation errors.

    This is very basic class, no specific outputs or other things which
    happened somewhere else. Just put an error message and then print it in
    template for example.
    """


# First inject WebOb exceptions
inject_exceptions(webob_exceptions, locals())

# Next routr exceptions, but without overwriting original WebOb exceptions
inject_exceptions(routr_exceptions, locals(), False)
