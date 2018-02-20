import os
from unittest import TestCase

from webtest import TestApp

from brochure_wsgi.brochure_wsgi_application import get_brochure_wsgi_application


class TestHTMLRequests(TestCase):

    def setUp(self):
        super().setUp()
        web_application = get_brochure_wsgi_application()
        os.environ["BROCHURE_ENTERPRISE"] = '{"name": "Example Enterprise"}'
        os.environ["BROCHURE_CONTACT_METHOD"] = '{"contact_method_type": "email", "value": "ejemplo@example.com"}'
        self.app = TestApp(web_application)

    def test_homepage_title_contains_enterprise_name(self):
        html = self.app.get("/").html

        self.assertEqual(html.title.text, "Example Enterprise")

    def test_homepage_header_contains_enterprise_name(self):
        html = self.app.get("/").html

        self.assertEqual(html.header.h1.text, "Example Enterprise")

    def test_homepage_footer_comtains_contact_method(self):
        html = self.app.get("/").html

        self.assertTrue("Email: ejemplo@example.com" in html.footer.p.text,
                        "Actual footer text: '{}'".format(html.footer.p.text))

    def test_random_path_returns_not_found(self):
        self.app.get("/asdf", status=404)

    def test_not_found_page_title_contains_enterprise_name(self):
        html = self.app.get("/zxcv", status=404).html

        self.assertEqual(html.title.text, "Example Enterprise | 404")

    def test_not_found_page_body_contains_not_found_message(self):
        html = self.app.get("/qwer", status=404).html

        self.assertEqual(html.body.h2.text, "404 Not Found")

    def test_not_found_page_body_contains_path(self):
        html = self.app.get("/qwer", status=404).html

        self.assertEqual(html.body.p.text, "Resource \"/qwer\" not found.")

    def test_not_found_page_comtains_contact_method(self):
        html = self.app.get("/fdsa", status=404).html

        self.assertTrue("Email: ejemplo@example.com" in html.footer.p.text,
                        "Actual footer text: '{}'".format(html.footer.p.text))

    def test_raise_exception_still_shows_page_title(self):
        self.app.app._brochure_application._command_map = None
        html = self.app.get("/", status=500).html

        self.assertEqual("Example Enterprise | 500", html.title.text)

    def test_raise_exception_still_shows_contact_method(self):
        self.app.app._brochure_application._command_map = None
        html = self.app.get("/", status=500).html

        self.assertTrue("Email: ejemplo@example.com" in html.footer.p.text,
                        "Actual footer text: '{}'".format(html.footer.p.text))

    def test_raise_exception_body_contains_error_message(self):
        self.app.app._brochure_application._command_map = None
        html = self.app.get("/", status=500).html

        self.assertEqual(html.body.h2.text, "500 Internal Server Error")

    def test_favicon(self):
        self.app.get("/favicon.ico")
