from abc import ABCMeta, abstractmethod
from typing import Dict, Callable, Optional


class CommandPreprocessor(metaclass=ABCMeta):  # pragma: no cover
    @abstractmethod
    def preprocess(self,
                   environ: Dict,
                   start_response: Callable) -> Optional[Callable[[Dict, Callable], str]]:
        pass
