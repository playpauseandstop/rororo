from rororo.app import create_app

from . import settings


app = create_app(settings)
