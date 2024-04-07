from typing import Callable, Awaitable

from hachiko.hachiko import AIOWatchdog, AIOEventHandler
from watchdog.events import FileCreatedEvent


class EventHandler(AIOEventHandler):
    def __init__(self, api_handler: Callable[[FileCreatedEvent], Awaitable[None]]) -> None:
        self.api_handler = api_handler
        super().__init__()

    async def on_created(self, event) -> None:
        if isinstance(event, FileCreatedEvent):
            await self.api_handler(event)


async def watch_for(path: str, handler: Callable[[FileCreatedEvent], Awaitable[None]]) -> Awaitable[AIOWatchdog]:
    watch = AIOWatchdog(path, event_handler=EventHandler(handler))
    watch.start()
    return watch
