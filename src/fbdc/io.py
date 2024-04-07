from typing import Any


class Base:
    def __init__(self, type: str, **kwargs: dict[str, Any]) -> None:
        self.type: str = type
        self.fields: dict[str, Any] = kwargs


class Request(Base):
    pass


class Response(Base):
    pass
