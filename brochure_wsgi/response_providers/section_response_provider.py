from typing import Dict, Callable

from brochure.values.basics import Basics
from brochure.values.section import Section
from jinja2 import Template
from werkzeug.wrappers import Response


class SectionResponseProvider(object):

    def __init__(self,
                 template: Template,
                 section_context_serializer: Callable[[Section, Basics], Dict[str, Dict[str, str]]],
                 response_serializer: Callable[[str], Response]) -> None:
        self._template = template
        self._section_context_serializer = section_context_serializer
        self._serializer = response_serializer
        super().__init__()

    def __call__(self, cover_section: Section, basics: Basics, *args, **kwargs) -> Response:
        context = self._section_context_serializer(cover_section, basics)
        body = self._template.render(context)
        response = self._serializer(body)

        return response
