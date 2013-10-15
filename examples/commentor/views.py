import datetime
import uuid

from app import app, redis


def add_comment(author, text):
    """
    Add new comment to Redis.
    """
    comment = {'author': author,
               'text': text,
               'time': format(datetime.datetime.now(),
                              app.settings.DATETIME_FORMAT)}
    key = app.settings.REDIS_COMMENT_KEY_PATTERN.format(uuid=str(uuid.uuid4()))

    with redis.pipeline() as pipe:
        pipe.hmset(key, comment)
        pipe.rpush(app.settings.REDIS_COMMENTS_KEY, key)
        pipe.execute()

    comment.update({'added': True})
    return comment


def comments(limit=None, offset=None):
    """
    Read all possible comments from Redis and show them on web page.
    """
    limit = limit or app.settings.COMMENTS_PER_PAGE
    return {}
