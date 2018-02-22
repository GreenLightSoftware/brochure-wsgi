import os
from unittest import TestCase

from webtest import TestApp

from brochure_wsgi.brochure_wsgi_application import get_brochure_wsgi_application


class TestJSONRequests(TestCase):

    def setUp(self):
        super().setUp()
        web_application = get_brochure_wsgi_application()
        os.environ['BROCHURE_ENTERPRISE'] = '{"name": "Example Enterprise"}'
        os.environ['BROCHURE_CONTACT_METHOD'] = '{"contact_method_type": "email", "value": "ejemplo@example.com"}'
        self.app = TestApp(web_application)

    def test_homepage_title_contains_enterprise_name(self):
        response = self.app.get('/', headers={'Accept': 'application/json'})

        expected_response_body = {
            "enterprise": {"name": "Example Enterprise"},
            "contact_method": {"contact_method_type": "email",
                               "display_name": "Email",
                               "value": "ejemplo@example.com"}
        }
        self.assertEqual(expected_response_body, response.json_body)

    def test_random_path_returns_not_found_and_shows_basics(self):
        response = self.app.get('/asdf', headers={'Accept': 'application/json'}, status=404)

        expected_response_body = {
            "error": "Resource '/asdf' not found.",
            "enterprise": {"name": "Example Enterprise"},
            "contact_method": {"contact_method_type": "email",
                               "display_name": "Email",
                               "value": "ejemplo@example.com"}
        }
        self.assertEqual(expected_response_body, response.json_body)

    def test_raise_exception_still_shows_basics(self):
        self.app.app._brochure_application._command_map = None
        response = self.app.get("/", headers={'Accept': 'application/json'}, status=500)

        expected_response_body = {
            "error": "'NoneType' object is not subscriptable",
            "enterprise": {"name": "Example Enterprise"},
            "contact_method": {"contact_method_type": "email",
                               "display_name": "Email",
                               "value": "ejemplo@example.com"}
        }

        self.assertEqual(expected_response_body, response.json_body)
