from typing import Dict, Callable

from brochure.values.basics import Basics
from jinja2 import Template
from werkzeug.wrappers import Response


class NotFoundResponseProvider(object):

    def __init__(self,
                 template: Template,
                 basics_context_serializer: Callable[[Basics], Dict[str, Dict[str, str]]],
                 response_serializer: Callable[[str], Response]) -> None:
        self._template = template
        self._basics_context_serializer = basics_context_serializer
        self._serializer = response_serializer
        super().__init__()

    def __call__(self, basics: Basics, path: str, *args, **kwargs) -> Response:
        body = self._get_body(basics=basics, path=path)
        response = self._serializer(body)

        return response

    def _get_body(self, basics: Basics, path: str):
        context = self._basics_context_serializer(basics)
        if path is not None:
            context = {**context, **{"path": path}}
        body = self._template.render(context)

        return body
