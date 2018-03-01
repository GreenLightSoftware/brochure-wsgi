import json
from collections import defaultdict
from functools import partial
from typing import Callable, Optional, Dict

from brochure.brochure_user_interface import BrochureUserInterface
from brochure.values.basics import Basics
from brochure.values.contact_method import ContactMethodType
from brochure.values.section import Section
from jinja2 import Environment, PackageLoader, select_autoescape
from werkzeug.wrappers import Response

from brochure_wsgi.response_providers.exception_response_provider import ExceptionReponseProvider
from brochure_wsgi.response_providers.not_found_response_provider import NotFoundResponseProvider
from brochure_wsgi.response_providers.section_response_provider import SectionResponseProvider


class HTTPUserInterface(BrochureUserInterface):

    def __init__(self,
                 section_response_provider: Callable[[Section, Basics], Response],
                 not_found_response_provider: Callable[[Basics], Response],
                 exception_response_provider: Callable[[Exception, Optional[Basics]], Response]) -> None:
        self._response = None
        self._section_response_provider = section_response_provider
        self._not_found_response_provider = not_found_response_provider
        self._exception_response_provider = exception_response_provider
        super().__init__()

    def get_response(self) -> Response:
        return self._response

    def show_unknown_command(self, basics: Basics) -> None:
        self._response = self._not_found_response_provider(basics)

    def show_cover(self, cover_section: Section, basics: Basics) -> None:
        self._response = self._section_response_provider(cover_section, basics)

    def show_unexpected_exception(self, exception: Exception, basics: Optional[Basics]) -> None:
        self._response = self._exception_response_provider(exception, basics)


class HTTPUserInterfaceProvider(object):

    def __init__(self):
        super().__init__()

        html_template_provider = Environment(
            loader=PackageLoader('brochure_wsgi', 'templates'),
            autoescape=select_autoescape(('html',))
        )

        def html_serializer(body: str, status: int) -> Response:
            return Response(body, mimetype="text/html", status=status)

        def status_code_html_serializer_provider(status: int) -> Callable[[str], Response]:
            return lambda body: html_serializer(body=body, status=status)

        def json_serializer(body: str, status: int) -> Response:
            return Response(body, mimetype="application/json", status=status)

        def status_code_json_serializer_provider(status: int) -> Callable[[str], Response]:
            return lambda body: json_serializer(body=body, status=status)

        def basics_context_serializer(basics: Basics) -> Dict[str, Dict[str, str]]:
            contact_method_dictionary = {}
            if basics.contact_method.contact_method_type == ContactMethodType.EMAIL:  # pragma nocover
                contact_method_dictionary["display_name"] = "Email"
                contact_method_dictionary["contact_method_type"] = "email"
                contact_method_dictionary["value"] = basics.contact_method.value
            # noinspection PyProtectedMember
            context = {"enterprise": basics.enterprise._asdict(),
                       "contact_method": contact_method_dictionary}

            return context

        def section_context_serializer(section: Section, basics: Basics) -> Dict[str, Dict[str, str]]:
            basics_dictionary = basics_context_serializer(basics)
            # noinspection PyProtectedMember
            context = {**basics_dictionary, **{"section": section._asdict()}}

            return context

        ok_html_serializer = status_code_html_serializer_provider(200)
        not_found_html_serializer = status_code_html_serializer_provider(404)

        ok_json_serializer = status_code_json_serializer_provider(200)
        not_found_json_serializer = status_code_json_serializer_provider(404)
        exception_json_serializer = status_code_json_serializer_provider(500)

        index_template = html_template_provider.get_template("section.html")
        not_found_template = html_template_provider.get_template("not_found.html")
        exception_template = html_template_provider.get_template("exception.html")
        section_response_html_provider = SectionResponseProvider(template=index_template,
                                                                 section_context_serializer=section_context_serializer,
                                                                 response_serializer=ok_html_serializer)
        not_found_response_html_provider = NotFoundResponseProvider(
            template=not_found_template,
            basics_context_serializer=basics_context_serializer,
            response_serializer=not_found_html_serializer)
        exception_response_html_provider = ExceptionReponseProvider(
            template=exception_template,
            basics_context_serializer=basics_context_serializer,
            response_serializer=html_serializer)

        def section_response_json_provider(section: Section, basics: Basics) -> Response:
            section_dictionary = section_context_serializer(section, basics)

            return ok_json_serializer(json.dumps(section_dictionary))

        def not_found_response_json_provider(basics: Basics, path: str) -> Response:
            dictionary = basics_context_serializer(basics)
            dictionary["error"] = "Resource '{}' not found.".format(path)

            return not_found_json_serializer(json.dumps(dictionary))

        def exception_response_json_provider(exception: Exception, basics: Optional[Basics]) -> Response:
            dictionary = basics_context_serializer(basics)
            dictionary["error"] = str(exception)

            return exception_json_serializer(json.dumps(dictionary))

        def html_response_provider(path: str) -> HTTPUserInterface:
            not_found_response_provider = partial(not_found_response_html_provider, **{"path": path})
            return HTTPUserInterface(section_response_provider=section_response_html_provider,
                                     not_found_response_provider=not_found_response_provider,
                                     exception_response_provider=exception_response_html_provider)

        def json_interface_provider(path: str) -> HTTPUserInterface:
            return HTTPUserInterface(
                section_response_provider=section_response_json_provider,
                not_found_response_provider=partial(not_found_response_json_provider, **{"path": path}),
                exception_response_provider=exception_response_json_provider)

        self._accept_map = defaultdict(lambda: html_response_provider)
        self._accept_map["application/json"] = json_interface_provider

    def __call__(self, path: str, accept: Optional[str]) -> HTTPUserInterface:
        return self._accept_map[accept](path)
