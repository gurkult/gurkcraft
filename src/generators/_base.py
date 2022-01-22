from abc import ABC, abstractmethod
from pathlib import Path

import dataclasses


@dataclasses.dataclass
class GeneratorResult:
    setup_hooks: list[str] = dataclasses.field(default_factory=list)
    tick_hooks: list[str] = dataclasses.field(default_factory=list)


class GeneratorError(Exception):
    pass


class BaseGenerator(ABC):
    name: str

    SOURCE = Path(".") / "src"
    META = SOURCE / "meta"
    EXTERNAL = SOURCE / "external"

    BUILD = Path(".") / "build"
    INTERMEDIATE = BUILD / "intermediate"
    PACK = BUILD / "gurkpack"

    NAMESPACE = PACK / "data" / "generated"
    FUNCTIONS = NAMESPACE / "functions"

    @abstractmethod
    def generate(self) -> GeneratorResult:
        pass

    @staticmethod

    def _format_command(command_: str, **kwargs: str|int|float) -> str:
        for key, value in kwargs.items():
            command_ = command_.replace(f"${key}", str(value))
        return command_
