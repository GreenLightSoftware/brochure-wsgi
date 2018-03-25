from typing import Tuple, Collection
from unittest import TestCase

from brochure_wsgi.command_preprocessors.upgrade_to_ssl_preprocessor import UpgradeToSSLPreprocessor


class TestUpgradeToSSLPreprocessor(TestCase):

    def setUp(self):
        super().setUp()
        self._start_response_called = False
        self._response_body = None
        self._response_headers = None

    def _fake_start_response(self,
                             response: str,
                             response_headers: Collection[Tuple[str, str]]):
        self._start_response_called = True
        self._response_body = response
        self._response_headers = response_headers

    def test_preprocess_when_already_secure_returns_none(self):
        preprocessor = UpgradeToSSLPreprocessor(is_insecure=lambda e: False,
                                                url_from_environment=lambda e: "my-special-secure-url")

        response_handler = preprocessor.preprocess(environ={}, start_response=lambda: None)

        self.assertIsNone(response_handler)

    def test_preprocess_when_already_secure_does_not_call_start_response(self):
        preprocessor = UpgradeToSSLPreprocessor(is_insecure=lambda e: False,
                                                url_from_environment=lambda e: "my-special-secure-url")

        preprocessor.preprocess(environ={}, start_response=self._fake_start_response)

        self.assertFalse(self._start_response_called)

    def test_preprocess_when_insecure_returns_callable_that_when_called_sets_response_body(self):
        preprocessor = UpgradeToSSLPreprocessor(is_insecure=lambda e: True,
                                                url_from_environment=lambda e: "http://www.example.com/asdf?q")

        response_handler = preprocessor.preprocess(environ={}, start_response=self._fake_start_response)
        response_handler({}, self._fake_start_response)

        self.assertEqual("301 Moved Permanently", self._response_body)

    def test_preprocess_when_insecure_returns_callable_that_when_called_sets_one_response_header(self):
        preprocessor = UpgradeToSSLPreprocessor(is_insecure=lambda e: True,
                                                url_from_environment=lambda e: "http://www.example.com/asdf?q")

        response_handler = preprocessor.preprocess(environ={}, start_response=self._fake_start_response)
        response_handler({}, self._fake_start_response)

        self.assertEqual(1, len(self._response_headers))

    def test_preprocess_when_insecure_returns_callable_that_when_called_sets_location_response_header(self):
        preprocessor = UpgradeToSSLPreprocessor(is_insecure=lambda e: True,
                                                url_from_environment=lambda e: "http://www.example.com/asdf?q")

        response_handler = preprocessor.preprocess(environ={}, start_response=self._fake_start_response)
        response_handler({}, self._fake_start_response)

        self.assertEqual(("Location", "https://www.example.com/asdf?q"), self._response_headers[0])
