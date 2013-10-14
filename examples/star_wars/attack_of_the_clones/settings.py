from rororo.routes import GET


ROUTES = (
    '/attack_of_the_clones',
    GET('/', 'attack_of_the_clones.views.index', name='index',
        renderer='attack_of_the_clones.html'),
)
