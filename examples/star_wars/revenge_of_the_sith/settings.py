from rororo import GET


ROUTES = (
    '/revenge_of_the_sith/',
    GET('/', 'revenge_of_the_sith.views.index', name='index',
        renderer='revenge_of_the_sith.html'),
)
