from typing import Dict, Callable, Optional, Collection
from urllib.parse import urlsplit, urlunsplit

from brochure_wsgi.command_preprocessors.command_preprocessor import CommandPreprocessor


class DomainRedirectPreprocessor(CommandPreprocessor):

    def __init__(self, url_from_environment: Callable[[Dict], str],
                 source_domain_provider: Callable[[], Collection[str]], target_domain_provider: Callable[[], str]) -> None:
        super().__init__()
        self._url_from_environment = url_from_environment
        self._source_domain_provider = source_domain_provider
        self._target_domain_provider = target_domain_provider

    def preprocess(self,
                   environ: Dict,
                   start_response: Callable) -> Optional[Callable[[Dict, Callable], str]]:
        source_url = self._url_from_environment(environ)
        source_scheme, source_domain, source_path, source_query, source_fragment = urlsplit(url=source_url)
        source_domains = self._source_domain_provider()

        if source_domain in source_domains:
            destination_domain = self._target_domain_provider()
            secure_destination_url = urlunsplit(("https", destination_domain, source_path, source_query, source_fragment))

            def redirect_to(environment: Dict, start_response_callable: Callable):
                start_response("301 Moved Permanently", [("Location", secure_destination_url)])

                return ""

            return redirect_to
