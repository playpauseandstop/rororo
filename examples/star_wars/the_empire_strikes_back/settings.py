from rororo import GET


ROUTES = ('/the_empire_stirkes_back',
    GET('/', lambda: {}, name='index', renderer='the_empire_strikes_back.html')
)
