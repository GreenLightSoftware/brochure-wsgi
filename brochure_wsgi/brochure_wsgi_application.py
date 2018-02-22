import os
from functools import partial
from typing import Callable, Optional, Dict, Tuple

from brochure.brochure_application import BrochureApplication
from brochure.commands.command_types import CommandType
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response
from whitenoise import WhiteNoise

from brochure_wsgi.http_user_interface import HTTPUserInterface, HTTPUserInterfaceProvider
from brochure_wsgi.value_fetchers.environment_contact_method_fetcher import environment_contact_method_fetcher
from brochure_wsgi.value_fetchers.environment_enterprise_fetcher import environment_enterprise_fetcher


def get_favicon_handler(favicon_url_path: str, favicon_file_path: str) -> Callable[[Dict, Callable], Response]:
    favicon_whitenoise = WhiteNoise(None)
    favicon_static_file = favicon_whitenoise.get_static_file(path=favicon_file_path, url=favicon_url_path)
    favicon_whitenoise.files[favicon_url_path] = favicon_static_file

    return partial(favicon_whitenoise.serve, static_file=favicon_static_file)


class GetRequestPathCommandProvider(object):
    def __init__(self, url_map: Map) -> None:
        super().__init__()
        self._url_map = url_map

    def __call__(self, environ: Dict, *args, **kwargs) -> Callable[[], Tuple[CommandType, Dict]]:
        def _command_provider() -> Tuple[CommandType, Dict]:
            map_adapter = self._url_map.bind_to_environ(environ)
            try:
                command_type_provider, command_parameters = map_adapter.match()
                command_type = command_type_provider()

                return command_type, command_parameters
            except NotFound:
                return CommandType.UNKNOWN, {}

        return _command_provider


class BrochureWSGIApplication(object):
    """
    WSGI application that wraps the brochure application.

    Each incoming HTTP request will invoke __call__ with request data inside `environ`.

    The `BrochureWSGIApplication` will then:
        - Handle any "web-only" application features (i.e favicons)
        - Register a new `UserInterface` object with the brochure application
        - Turn the incoming request into a command (using the `GetRequestPathCommandProvider`) and feed it into the
          application
        - Internally, the domain application injects its repsonse into the `HTTPUserInterface`
        - Use the `HTTPUserInterface` to generate a werkzeug `Response` callable
        - Call the `Response` callable and return its result
    """

    def __init__(self,
                 favicon_handler: Callable,
                 favicon_url_path: str,
                 brochure_application: BrochureApplication,
                 user_interface_provider: Callable[[str, Optional[str]], HTTPUserInterface],
                 get_web_command_provider: GetRequestPathCommandProvider):
        super().__init__()
        self._favicon_url_path = favicon_url_path
        self._favicon_handler = favicon_handler
        self._brochure_application = brochure_application
        self._user_interface_provider = user_interface_provider
        self._get_web_command_provider = get_web_command_provider

    def __call__(self, environ, start_response):
        maybe_response = self._handle_non_domain_application_request(environ, start_response)
        if maybe_response is not None:
            return maybe_response
        path = environ.get("PATH_INFO")
        maybe_accept = environ.get("HTTP_ACCEPT")
        user_interface = self._user_interface_provider(path, maybe_accept)
        self._brochure_application.register_user_interface(user_interface=user_interface)

        web_command_provider = self._get_web_command_provider(environ=environ)
        self._brochure_application.process_command(command_provider=web_command_provider)

        response = user_interface.get_response()

        return response(environ=environ, start_response=start_response)

    def _handle_non_domain_application_request(self, environ, start_response) -> Optional[Response]:
        if environ.get("PATH_INFO") == self._favicon_url_path:
            return self._favicon_handler(**{"environ": environ, "start_response": start_response})
        return None


def get_brochure_wsgi_application() -> BrochureWSGIApplication:
    url_map = Map()
    url_map.add(Rule("/", endpoint=lambda: CommandType.SHOW_BASICS))
    favion_url_path = "/favicon.ico"

    favicon_file_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "static"), "favicon.ico")
    favicon_handler = get_favicon_handler(favicon_url_path=favion_url_path, favicon_file_path=favicon_file_path)
    domain_application = BrochureApplication(contact_method_fetcher=environment_contact_method_fetcher,
                                             enterprise_fetcher=environment_enterprise_fetcher)
    get_web_command_provider = GetRequestPathCommandProvider(url_map=url_map)
    user_interface_provider = HTTPUserInterfaceProvider()

    return BrochureWSGIApplication(favicon_handler=favicon_handler,
                                   favicon_url_path=favion_url_path,
                                   brochure_application=domain_application,
                                   user_interface_provider=user_interface_provider,
                                   get_web_command_provider=get_web_command_provider)
