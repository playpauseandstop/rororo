from rororo import GET


JINJA_FILTERS = {
    'the_empire_strikes_back': 'Episode V: {0}'.format
}
ROUTES = (
    '/the_empire_strikes_back',
    GET('/', lambda: {'title': 'The Empire Strikes Back'}, name='index',
        renderer='the_empire_strikes_back.html')
)
