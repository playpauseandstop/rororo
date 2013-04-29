try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from rororo.manager import pep8
from webtest import TestApp

from .app import app


class TestStarWars(TestCase):

    def setUp(self):
        self.app = TestApp(app)

        self.index_url = app.reverse('index')
        self.urls = {}

        for package in app.packages:
            self.urls[package] = app.reverse('{0}:index'.format(package))

    def test_all_episodes(self):
        response = self.app.get(self.index_url, status=200)
        self.assertIn(self.urls['a_new_hope'], response.ubody)
        self.assertIn(self.urls['the_empire_strikes_back'], response.ubody)
        self.assertIn(self.urls['return_of_the_jedi'], response.ubody)
        self.assertIn(self.urls['the_phantom_menace'], response.ubody)
        self.assertIn(self.urls['attack_of_the_clones'], response.ubody)
        self.assertIn(self.urls['revenge_of_the_sith'], response.ubody)

    def test_all_episodes_css(self):
        url = app.reverse('static', 'css/star_wars.css')
        self.app.get(url, status=200)

        for package in app.packages:
            url = app.reverse('static', 'css/{0}.css'.format(package))
            self.app.get(url, status=200)

    def test_episode_i(self):
        response = self.app.get(self.urls['the_phantom_menace'], status=200)
        self.assertIn(
            '<h1><a href="{0}">Star Wars</a></h1>'.format(self.index_url),
            response.ubody
        )
        self.assertIn('<h2>Episode I: The Phantom Menace</h2>', response.ubody)

    def test_episode_ii(self):
        response = self.app.get(self.urls['attack_of_the_clones'], status=200)
        self.assertIn(
            '<h1><a href="{0}">Star Wars</a></h1>'.format(self.index_url),
            response.ubody
        )
        self.assertIn(
            '<h2>Episode II: Attack of the Clones</h2>', response.ubody
        )

    def test_episode_iii(self):
        response = self.app.get(self.urls['revenge_of_the_sith'], status=200)
        self.assertIn(
            '<h1><a href="{0}">Star Wars</a></h1>'.format(self.index_url),
            response.ubody
        )
        self.assertIn(
            '<h2>Episode III: Revenge of the Sith</h2>', response.ubody
        )

    def test_episode_iv(self):
        response = self.app.get(self.urls['a_new_hope'], status=200)
        self.assertIn(
            '<h1><a href="{0}">Star Wars</a></h1>'.format(self.index_url),
            response.ubody
        )
        self.assertIn('<h2>Episode IV: A New Hope</h2>', response.ubody)

    def test_episode_v(self):
        response = self.app.get(self.urls['the_empire_strikes_back'],
                                status=200)
        self.assertIn(
            '<h1><a href="{0}">Star Wars</a></h1>'.format(self.index_url),
            response.ubody
        )
        self.assertIn(
            '<h2>Episode V: The Empire Strikes Back</h2>', response.ubody
        )

    def test_episode_vi(self):
        response = self.app.get(self.urls['return_of_the_jedi'], status=200)
        self.assertIn(
            '<h1><a href="{0}">Star Wars</a></h1>'.format(self.index_url),
            response.ubody
        )
        self.assertIn(
            '<h2>Episode VI: Return of the Jedi</h2>', response.ubody
        )

    def test_pep8(self):
        report = pep8(app, True)
        self.assertEqual(report.total_errors, 0)
