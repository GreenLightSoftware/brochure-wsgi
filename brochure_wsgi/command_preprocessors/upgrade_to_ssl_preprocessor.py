from typing import Dict, Callable, Optional, Any
from urllib.parse import urlunsplit, urlsplit

from brochure_wsgi.command_preprocessors.command_preprocessor import CommandPreprocessor


class UpgradeToSSLPreprocessor(CommandPreprocessor):

    def __init__(self,
                 is_insecure: Callable[[Dict], bool],
                 url_from_environment: Callable[[Dict], str]) -> None:
        super().__init__()
        self._is_insecure = is_insecure
        self._url_from_environment = url_from_environment

    def preprocess(self,
                   environ: Dict,
                   start_response: Callable) -> Optional[Callable[[Dict, Callable], str]]:
        if self._is_insecure(environ):
            insecure_source_url = self._url_from_environment(environ)
            redirect_to_secure_url = self._get_redirect_to(source_url=insecure_source_url,
                                                           start_response=start_response)

            return redirect_to_secure_url

    @staticmethod
    def _get_redirect_to(source_url: str,
                         start_response: Callable) -> Callable[[Any], str]:
        scheme, netloc, path, query, fragment = urlsplit(url=source_url)
        secure_destination_url = urlunsplit(("https", netloc, path, query, fragment))

        def redirect_to():
            start_response("301 Moved Permanently", [("Location", secure_destination_url)])

            return ""

        return redirect_to
