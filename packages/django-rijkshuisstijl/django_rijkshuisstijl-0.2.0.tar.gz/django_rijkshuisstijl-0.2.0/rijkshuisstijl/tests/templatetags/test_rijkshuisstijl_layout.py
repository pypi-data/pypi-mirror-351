from django.template import Context, Template
from django.test import RequestFactory, TestCase

from rijkshuisstijl.tests.templatetags.utils import InclusionTagWebTest


class NavigationBarTestCase(InclusionTagWebTest):
    def test_navigation_bar(self):
        config = Context({"request": RequestFactory().get("/foo")})
        html = (
            Template(
                '{% load rijkshuisstijl %}{% block navigation %}{% navigation_bar %}{% endblock %}'
            )
            .render(config)
        )

        self.assertInHTML(
            '<nav class="navigation-bar"><div class="navigation-bar__body">'
            '<div class="login-bar"><p class="login-bar__body">'
            '<a class="login-bar__link login-bar__link--primary" href="/accounts/login/">Inloggen</a>'
            '</p></div><ul class="menu"></ul></div></nav>',
            html,
            count=1
        )

    def test_breadcrumb_override(self):
        config = Context({"request": RequestFactory().get("/foo")})
        html = (
            Template(
                '{% load rijkshuisstijl %}{% block navigation %}'
                '{% navigation_bar show_breadcrumbs=False %}'
                '<ul class="custom-breadcrumbs"><li>Item 1</li><li>Item 2</li></ul>{% endblock %}'
            )
            .render(config)
        )

        self.assertInHTML(
            '<nav class="navigation-bar"><div class="navigation-bar__body">'
            '<div class="login-bar"><p class="login-bar__body">'
            '<a class="login-bar__link login-bar__link--primary" href="/accounts/login/">Inloggen</a>'
            '</p></div><ul class="menu"></ul></div></nav><ul class="custom-breadcrumbs"><li>Item 1</li><li>Item 2</li></ul>',
            html,
            count=1
        )
