from star_wars.app import app


def index():
    """
    Episode I: The Phantom Menace
    """
    return {'index_url': app.reverse('index')}
