from typing import Dict, Callable, Tuple

from brochure.commands.command_types import CommandType
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map


class GetPathCommandProvider(object):
    """
    Returns a callable that maps web input to domain application input.

    Takes in data from an HTTP request (the contents of the `environ` parameter: path, method, body,
    etc) and returns a command type and associated command parameters for the brochure application.
    """

    def __init__(self, url_map: Map) -> None:
        super().__init__()
        self._url_map = url_map

    def __call__(self, environ: Dict) -> Callable[[], Tuple[CommandType, Dict]]:
        def _command_provider() -> Tuple[CommandType, Dict]:
            map_adapter = self._url_map.bind_to_environ(environ)
            try:
                command_type_provider, command_parameters = map_adapter.match()
                command_type = command_type_provider()

                return command_type, command_parameters
            except NotFound:
                return CommandType.UNKNOWN, {}

        return _command_provider
