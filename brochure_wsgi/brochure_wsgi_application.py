import os
from typing import Callable, Optional, Iterable

from brochure.brochure_application import BrochureApplication
from brochure.commands.command_types import CommandType
from werkzeug.routing import Map, Rule

from brochure_wsgi.command_preprocessors.command_preprocessor import CommandPreprocessor
from brochure_wsgi.command_preprocessors.favicon_preprocessor import FaviconPreprocessor
from brochure_wsgi.http_user_interface import HTTPUserInterface, HTTPUserInterfaceProvider
from brochure_wsgi.path_command_provider import GetPathCommandProvider
from brochure_wsgi.value_fetchers.environment_contact_method_fetcher import environment_contact_method_fetcher
from brochure_wsgi.value_fetchers.environment_cover_section_fetcher import environment_cover_section_fetcher
from brochure_wsgi.value_fetchers.environment_enterprise_fetcher import environment_enterprise_fetcher


class BrochureWSGIApplication(object):
    """
    WSGI application that wraps the brochure application.

    Each incoming HTTP request will invoke `__call__` with request data inside `environ`.

    The `BrochureWSGIApplication` will then:
        - Handle any "web-only" application features (i.e favicons)
        - Register a new `UserInterface` object with the brochure application
        - Turn the incoming request into a brochure application command (using the `GetPathCommandProvider`) and
          feed it into the application's `process_command` method.
        - Internally, the domain application injects its response into the `HTTPUserInterface`
        - Use the `HTTPUserInterface` to generate a werkzeug `Response` callable
        - Call the `Response` callable and return its result
    """

    def __init__(self,
                 domain_application: BrochureApplication,
                 user_interface_provider: Callable[[str, Optional[str]], HTTPUserInterface],
                 get_path_command_provider: GetPathCommandProvider,
                 command_preprocessors: Optional[Iterable[CommandPreprocessor]] = None):
        super().__init__()
        self._domain_application = domain_application
        self._user_interface_provider = user_interface_provider
        self._get_path_command_provider = get_path_command_provider
        self._command_preprocessors = command_preprocessors

    def __call__(self, environ, start_response: Callable):
        for command_preprocessor in self._command_preprocessors or tuple():
            response_provider = command_preprocessor.preprocess(environ=environ, start_response=start_response)
            if response_provider is not None:
                return response_provider(environ=environ, start_response=start_response)

        path = environ.get("PATH_INFO")
        maybe_accept_header = environ.get("HTTP_ACCEPT")
        user_interface = self._user_interface_provider(path, maybe_accept_header)
        self._domain_application.register_user_interface(user_interface=user_interface)

        path_command_provider = self._get_path_command_provider(environ=environ)
        self._domain_application.process_command(command_provider=path_command_provider)
        response_provider = user_interface.get_response_provider()

        return response_provider(environ=environ, start_response=start_response)


def get_brochure_wsgi_application() -> BrochureWSGIApplication:
    brochure_application_command_map = Map()
    brochure_application_command_map.add(Rule("/", endpoint=lambda: CommandType.SHOW_COVER))
    get_path_command_provider = GetPathCommandProvider(url_map=brochure_application_command_map)

    domain_application = BrochureApplication(contact_method_fetcher=environment_contact_method_fetcher,
                                             cover_section_fetcher=environment_cover_section_fetcher,
                                             enterprise_fetcher=environment_enterprise_fetcher)
    user_interface_provider = HTTPUserInterfaceProvider()

    favicon_url_path = "/favicon.ico"
    static_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "static")
    favicon_file_path = os.path.join(static_file_path, "favicon.ico")
    favicon_preprocessor = FaviconPreprocessor(favicon_url_path=favicon_url_path,
                                               favicon_file_path=favicon_file_path,
                                               request_path_provider=lambda e: e.get("PATH_INFO"))
    command_preprocessors = (favicon_preprocessor,)

    return BrochureWSGIApplication(domain_application=domain_application,
                                   user_interface_provider=user_interface_provider,
                                   get_path_command_provider=get_path_command_provider,
                                   command_preprocessors=command_preprocessors)
