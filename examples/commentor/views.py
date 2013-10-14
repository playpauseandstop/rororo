from app import app


def add_comment(author, text):
    """
    Add new comment to Redis.
    """
    return app.redirect('comments')


def comments():
    """
    Read all possible comments from Redis and show them on web page.
    """
    return {}
