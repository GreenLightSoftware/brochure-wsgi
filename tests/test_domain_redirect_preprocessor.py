from typing import Collection, Tuple
from unittest import TestCase

from brochure_wsgi.command_preprocessors.domain_redirect_preprocessor import DomainRedirectPreprocessor


class TestDomainRedirectPreprocessor(TestCase):

    def setUp(self):
        super().setUp()

    def _fake_start_response(self,
                             response: str,
                             response_headers: Collection[Tuple[str, str]]):
        self._start_response_called = True
        self._response_body = response
        self._response_headers = response_headers

    def test_preprocess_when_no_source_urls_are_present(self):
        preprocessor = DomainRedirectPreprocessor(url_from_environment=lambda e: "http://www.example.com",
                                                  source_domain_provider=lambda: tuple(),
                                                  target_domain_provider=lambda e: "my-special-secure-url")

        response_handler = preprocessor.preprocess(environ={}, start_response=lambda: None)

        self.assertIsNone(response_handler)

    def test_preprocess_when_no_matching_source_url_is_present(self):
        preprocessor = DomainRedirectPreprocessor(url_from_environment=lambda e: "http://www.example.com",
                                                  source_domain_provider=lambda: ("example.com",),
                                                  target_domain_provider=lambda: "my-special-secure-url")

        response_handler = preprocessor.preprocess(environ={}, start_response=lambda: None)

        self.assertIsNone(response_handler)

    def test_preprocess_when_matching_source_url_is_present_sets_correct_http_status(self):
        preprocessor = DomainRedirectPreprocessor(url_from_environment=lambda e: "http://example.com",
                                                  source_domain_provider=lambda: ("example.com",),
                                                  target_domain_provider=lambda: "www.destination.com")

        response_handler = preprocessor.preprocess(environ={}, start_response=self._fake_start_response)
        response_handler({}, self._fake_start_response)

        self.assertEqual("301 Moved Permanently", self._response_body)

    def test_preprocess_when_matching_source_url_is_present_sets_correct_number_of_response_headers(self):
        preprocessor = DomainRedirectPreprocessor(url_from_environment=lambda e: "http://www.example.com",
                                                  source_domain_provider=lambda: ("www.example.com",),
                                                  target_domain_provider=lambda: "www.destination.com")

        response_handler = preprocessor.preprocess(environ={}, start_response=self._fake_start_response)
        response_handler({}, self._fake_start_response)

        self.assertEqual(1, len(self._response_headers))

    def test_preprocess_when_matching_source_url_is_present_sets_correct_location_response_header(self):
        preprocessor = DomainRedirectPreprocessor(url_from_environment=lambda e: "http://example.com/asdf?q",
                                                  source_domain_provider=lambda: ("example.com",),
                                                  target_domain_provider=lambda: "www.destination.com")

        response_handler = preprocessor.preprocess(environ={}, start_response=self._fake_start_response)
        response_handler({}, self._fake_start_response)

        self.assertEqual(("Location", "https://www.destination.com/asdf?q"), self._response_headers[0])
