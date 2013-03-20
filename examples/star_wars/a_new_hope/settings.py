from rororo import GET


JINJA_GLOBALS = {
    'a_new_hope': 'Episode IV: A New Hope',
}
ROUTES = (
    '/a_new_hope',
    GET('/', 'a_new_hope.views.index', name='index',
        renderer='a_new_hope.html'),
)
