from typing import Callable, Optional, Dict

from brochure.brochure_user_interface import BrochureUserInterface
from brochure.values.basics import Basics
from brochure.values.contact_method import ContactMethodType
from jinja2 import Environment, PackageLoader, select_autoescape
from werkzeug.wrappers import Response

from brochure_wsgi.response_providers.basics_response_provider import BasicsReponseProvider
from brochure_wsgi.response_providers.exception_response_provider import ExceptionReponseProvider


class HTMLUserInterface(BrochureUserInterface):

    def __init__(self,
                 environ: Dict,
                 basics_response_provider: Callable[[Basics], Response],
                 not_found_response_provider: Callable[[Basics], Response],
                 exception_response_provider: Callable[[Exception, Optional[Basics]], Response]) -> None:
        self._environ = environ
        self._response = None
        self._basics_response_provider = basics_response_provider
        self._not_found_response_provider = not_found_response_provider
        self._exception_response_provider = exception_response_provider
        super().__init__()

    def get_response(self) -> Response:
        return self._response

    def show_unknown_command(self, basics: Basics) -> None:
        self._response = self._not_found_response_provider(basics, environ=self._environ)

    def show_basics(self, basics: Basics) -> None:
        self._response = self._basics_response_provider(basics)

    def show_unexpected_exception(self, exception: Exception, basics: Optional[Basics]) -> None:
        self._response = self._exception_response_provider(exception, basics)


class HTMLUserInterfaceProvider(object):
    def __init__(self):
        template_provider = Environment(
            loader=PackageLoader('brochure_wsgi', 'templates'),
            autoescape=select_autoescape(('html',))
        )

        def html_serializer(body: str, status: int) -> Response:
            return Response(body, mimetype="text/html", status=status)

        def status_code_html_serializer_provider(status: int) -> Callable[[str], Response]:
            return lambda body: html_serializer(body=body, status=status)

        def basics_context_serializer(basics: Basics) -> Dict[str, Dict[str, str]]:
            contact_method_dictionary = {}
            if basics.contact_method.contact_method_type == ContactMethodType.EMAIL:  # pragma nocover
                contact_method_dictionary["display_name"] = "Email"
                contact_method_dictionary["contact_method_type"] = "email"
                contact_method_dictionary["value"] = basics.contact_method.value
            # noinspection PyProtectedMember
            context = {"enterprise": basics.enterprise._asdict(), "contact_method": contact_method_dictionary}

            return context

        ok_html_serializer = status_code_html_serializer_provider(200)
        not_found_html_serializer = status_code_html_serializer_provider(404)

        index_template = template_provider.get_template("index.html")
        not_found_template = template_provider.get_template("not_found.html")
        exception_template = template_provider.get_template("exception.html")
        self._basics_response_provider = BasicsReponseProvider(template=index_template,
                                                               basics_context_serializer=basics_context_serializer,
                                                               response_serializer=ok_html_serializer)
        self._not_found_response_provider = BasicsReponseProvider(template=not_found_template,
                                                                  basics_context_serializer=basics_context_serializer,
                                                                  response_serializer=not_found_html_serializer)
        self._exception_response_provider = ExceptionReponseProvider(
            template=exception_template,
            basics_context_serializer=basics_context_serializer,
            response_serializer=html_serializer)
        super().__init__()

    def __call__(self, environ: Dict, *args, **kwargs) -> HTMLUserInterface:
        return HTMLUserInterface(environ=environ,
                                 basics_response_provider=self._basics_response_provider,
                                 not_found_response_provider=self._not_found_response_provider,
                                 exception_response_provider=self._exception_response_provider)
