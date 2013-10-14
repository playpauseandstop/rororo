from rororo.routes import GET


ROUTES = (
    '',
    GET('/return_of_the_jedi/', lambda: {}, name='index',
        renderer='return_of_the_jedi.html'),
)
