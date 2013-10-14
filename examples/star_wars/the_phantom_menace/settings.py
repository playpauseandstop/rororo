from rororo.routes import GET


ROUTES = (
    GET('/the_phantom_menace/', 'the_phantom_menace.views.index', name='index',
        renderer='the_phantom_menace.html'),
)
