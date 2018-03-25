from functools import partial
from typing import Dict, Callable, Optional

from whitenoise import WhiteNoise

from brochure_wsgi.command_preprocessors.command_preprocessor import CommandPreprocessor


class FaviconPreprocessor(CommandPreprocessor):

    def __init__(self,
                 favicon_url_path: str,
                 favicon_file_path: str,
                 request_path_provider: Callable[[Dict], Optional[str]]) -> None:
        super().__init__()

        favicon_whitenoise = WhiteNoise(None)
        favicon_static_file = favicon_whitenoise.get_static_file(path=favicon_file_path, url=favicon_url_path)
        favicon_whitenoise.files[favicon_url_path] = favicon_static_file

        self._favicon_url_path = favicon_url_path
        self._favicon_handler = partial(favicon_whitenoise.serve, static_file=favicon_static_file)
        self._request_path_provider = request_path_provider

    def preprocess(self,
                   environ: Dict,
                   start_response: Callable[[Dict, Callable], str]) -> Optional[Callable[[Dict, Callable], str]]:
        path = self._request_path_provider(environ)
        if path == self._favicon_url_path:
            return self._favicon_handler
