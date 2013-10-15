import datetime
import uuid

from app import app, redis


def add_comment(author, text):
    """
    Add new comment to Redis.
    """
    comment = {'author': author,
               'datetime': format(datetime.datetime.now(),
                                  app.settings.DATETIME_FORMAT),
               'text': text}
    key = app.settings.REDIS_COMMENT_KEY_PATTERN.format(uuid=str(uuid.uuid4()))

    with redis.pipeline() as pipe:
        pipe.hmset(key, comment)
        pipe.lpush(app.settings.REDIS_COMMENTS_KEY, key)
        pipe.execute()

    return {'added': True}


def get_comments(limit=None):
    """
    Return latest comments from Redis.
    """
    limit = limit or app.settings.COMMENTS_PER_PAGE
    keys = redis.lrange(app.settings.REDIS_COMMENTS_KEY, 0, limit)

    with redis.pipeline() as pipe:
        map(pipe.hgetall, keys[::-1])
        comments = pipe.execute()

    return comments
