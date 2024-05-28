from abc import ABC, abstractmethod
from typing import Any, Awaitable


class BaseClient(ABC):
    async def init(self, data: dict[str, Any]) -> Awaitable[None]:
        pass

    @abstractmethod
    async def message(self, data: dict[str, Any]) -> Awaitable[None]:
        pass
