from rororo import GET


# Debug settings
DEBUG = True

# Available packages
PACKAGES = (
    'a_new_hope',
    'the_empire_strikes_back',
    'return_of_the_jedi',
    'the_phantom_menace',
    'attack_of_the_clones',
    'revenge_of_the_sith',
)

# Available routes
ROUTES = ('',
    GET('/', 'star_wars.views.index', name='index', renderer='index.html'),
)
