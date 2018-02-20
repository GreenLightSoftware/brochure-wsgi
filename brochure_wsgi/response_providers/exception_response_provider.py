from typing import Callable, Optional, Dict

from brochure.values.basics import Basics
from jinja2 import Template
from werkzeug.wrappers import Response


class ExceptionReponseProvider(object):
    def __init__(self,
                 template: Template,
                 basics_context_serializer: Callable[[Basics], Dict[str, Dict[str, str]]],
                 response_serializer: Callable[[str, int], Response]) -> None:
        self._template = template
        self._basics_context_serializer = basics_context_serializer
        self._response_serializer = response_serializer
        super().__init__()

    def __call__(self, exception: Exception, basics: Optional[Basics], *args, **kwargs) -> Response:
        basics_context = self._basics_context_serializer(basics) if basics is not None else {}
        exception_context = {"exception": exception}
        context = {**basics_context, **exception_context}
        body = self._template.render(context)

        return self._response_serializer(body, 500)
