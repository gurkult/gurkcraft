from abc import ABC, abstractmethod
from pathlib import Path

import dataclasses


@dataclasses.dataclass
class GeneratorResult:
    setup_hooks: list[str] = dataclasses.field(default_factory=list)
    tick_hooks: list[str] = dataclasses.field(default_factory=list)


class BaseGenerator(ABC):
    name: str

    META = Path(".") / "src" / "meta"

    PACK = Path(".") / "build" / "gurkpack"
    NAMESPACE = PACK / "data" / "generated"
    FUNCTIONS = NAMESPACE / "functions"

    @abstractmethod
    def generate(self) -> GeneratorResult:
        pass

    @staticmethod
    def _format_command(command: str, **kwargs: str) -> str:
        for key, value in kwargs.items():
            command = command.replace(f"${key}", str(value))
        return command
