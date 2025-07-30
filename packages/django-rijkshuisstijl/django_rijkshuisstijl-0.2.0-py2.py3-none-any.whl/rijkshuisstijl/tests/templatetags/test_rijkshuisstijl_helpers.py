from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory, Client

from rijkshuisstijl.templatetags.rijkshuisstijl_helpers import get_request_user


class HelpersTestCase(TestCase):
    def test_get_request_user_anon(self):
        request = RequestFactory()
        self.assertIsNone(getattr(request, 'user', None))
        actual = get_request_user(request)
        self.assertIsNotNone(actual)

    def test_get_request_user(self):
        User = get_user_model()
        user = User()
        request = RequestFactory()
        request.user = user
        actual = get_request_user(request)
        self.assertIsNotNone(actual)
        self.assertEqual(actual, user)
