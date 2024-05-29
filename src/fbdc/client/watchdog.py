"""
Custom watchdog for filesystem client

EventHandler(): thing that asynchronously watch for changes in file
watch_for(path: str, handler: Callable[[FileCreatedEvent], Awaitable[None]]) -> Awaitable[AIOWatchdog]: watch for path
"""

from typing import Callable, Awaitable

from hachiko.hachiko import AIOEventHandler, AIOWatchdog
from watchdog.events import FileCreatedEvent


class EventHandler(AIOEventHandler):
    """Thing that asynchronously watch for changes in file"""

    def __init__(self, api_handler: Callable[[FileCreatedEvent], Awaitable[None]]) -> None:
        """
        Thing that asynchronously watch for changes in file

        :param api_handler: Function that will be called if path will be created
        :type api_handler: Callable[[FileCreatedEvent], Awaitable[None]]
        :return: Returns nothing
        :rtype: None
        """

        self.api_handler = api_handler
        super().__init__()

    async def on_created(self, event: FileCreatedEvent) -> Awaitable[None]:
        """
        Call handler when path will be created

        :param event: event
        :type event: FileCreatedEvent
        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        if isinstance(event, FileCreatedEvent):
            await self.api_handler(event)


async def watch_for(path: str, handler: Callable[[FileCreatedEvent], Awaitable[None]]) -> Awaitable[AIOWatchdog]:
    """
    Watch for path

    :param path: Path to watch for
    :type path: str
    :param handler: Function that will be called if path will be created
    :type handler: Callable[[FileCreatedEvent], Awaitable[None]]
    :return: Returns watchdog
    :rtype: Awaitable[AIOWatchdog]
    """

    watch = AIOWatchdog(path, event_handler=EventHandler(handler))
    watch.start()
    return watch
