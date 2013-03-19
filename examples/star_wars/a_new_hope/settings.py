from rororo import GET


ROUTES = ('/a_new_hope',
    GET('/', 'a_new_hope.views.index', name='index',
        renderer='a_new_hope.html'),
)
