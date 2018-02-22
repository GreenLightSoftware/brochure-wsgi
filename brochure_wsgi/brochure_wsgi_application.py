import os
from functools import partial
from typing import Callable, Optional, Dict

from brochure.brochure_application import BrochureApplication
from brochure.commands.command_types import CommandType
from werkzeug.routing import Map, Rule
from whitenoise import WhiteNoise

from brochure_wsgi.http_user_interface import HTTPUserInterface, HTTPUserInterfaceProvider
from brochure_wsgi.path_command_provider import PathCommandProvider
from brochure_wsgi.value_fetchers.environment_contact_method_fetcher import environment_contact_method_fetcher
from brochure_wsgi.value_fetchers.environment_enterprise_fetcher import environment_enterprise_fetcher


class BrochureWSGIApplication(object):
    """
    WSGI application that wraps the brochure application.

    Each incoming HTTP request will invoke __call__ with request data inside `environ`.

    The `BrochureWSGIApplication` will then:
        - Handle any "web-only" application features (i.e favicons)
        - Register a new `UserInterface` object with the brochure application
        - Turn the incoming request into a brochure application command (using the `PathCommandProvider`) and
          feed it into the application's `process_command` method.
        - Internally, the domain application injects its response into the `HTTPUserInterface`
        - Use the `HTTPUserInterface` to generate a werkzeug `Response` callable
        - Call the `Response` callable and return its result
    """

    def __init__(self,
                 web_route_map: Dict[str, Callable],
                 domain_application: BrochureApplication,
                 user_interface_provider: Callable[[str, Optional[str]], HTTPUserInterface],
                 get_web_command_provider: PathCommandProvider):
        super().__init__()
        self._web_route_map = web_route_map
        self._domain_application = domain_application
        self._user_interface_provider = user_interface_provider
        self._get_web_command_provider = get_web_command_provider

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO")

        web_handler = self._web_route_map.get(path)
        if web_handler is not None:
            return web_handler(environ=environ, start_response=start_response)

        maybe_accept_header = environ.get("HTTP_ACCEPT")
        user_interface = self._user_interface_provider(path, maybe_accept_header)
        self._domain_application.register_user_interface(user_interface=user_interface)

        command_provider = self._get_web_command_provider(environ=environ)
        self._domain_application.process_command(command_provider=command_provider)

        response = user_interface.get_response()

        return response(environ=environ, start_response=start_response)


def get_brochure_wsgi_application() -> BrochureWSGIApplication:
    favicon_url_path = "/favicon.ico"
    favicon_file_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), "static"), "favicon.ico")
    favicon_whitenoise = WhiteNoise(None)
    favicon_static_file = favicon_whitenoise.get_static_file(path=favicon_file_path, url=favicon_url_path)
    favicon_whitenoise.files[favicon_url_path] = favicon_static_file
    favicon_handler = partial(favicon_whitenoise.serve, static_file=favicon_static_file)

    web_route_map = {favicon_url_path: favicon_handler}

    brochure_application_command_map = Map()
    brochure_application_command_map.add(Rule("/", endpoint=lambda: CommandType.SHOW_BASICS))
    get_web_command_provider = PathCommandProvider(url_map=brochure_application_command_map)

    domain_application = BrochureApplication(contact_method_fetcher=environment_contact_method_fetcher,
                                             enterprise_fetcher=environment_enterprise_fetcher)
    user_interface_provider = HTTPUserInterfaceProvider()

    return BrochureWSGIApplication(web_route_map=web_route_map,
                                   domain_application=domain_application,
                                   user_interface_provider=user_interface_provider,
                                   get_web_command_provider=get_web_command_provider)
