from redis import StrictRedis

from rororo.app import create_app
from rororo.manager import manage

import settings


app = create_app(settings)
redis = StrictRedis.from_url(app.settings.REDIS_URL)


if __name__ == '__main__':
    manage(app)
