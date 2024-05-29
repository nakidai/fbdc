"""
Filesystem client for fbdc

FSClient(root: str): filesystem client for fbdc
"""

from os import makedirs
from pathlib import Path
from typing import Any, Awaitable

import aiofiles
import aiofiles.os
from hachiko.hachiko import AIOWatchdog
from watchdog.events import FileCreatedEvent

from ..utils import set_root

from .base import BaseClient
from .watchdog import watch_for


class FSClient(BaseClient):
    """Filesystem client for fbdc"""

    def __init__(self, root: str) -> None:
        """
        Filesystem client for fbdc

        :param root: Root of the client
        :type root: str
        """

        self.root: str = root
        self.path: Callable[[str], str] = set_root(self.root)
        self.server_request: Callable[[Request], Awaitable[Response]] | None = None

        self.watchdogs: list[AIOWatchdog] = []

    async def channel_api_handler(self, event: FileCreatedEvent) -> Awaitable[None]:
        """
        Handle channel's api

        :param event: Request
        :type event: watchdog.events.FileCreatedEvent
        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        path = event.src_path.split('/')
        async with aiofiles.open(event.src_path) as f:
            content = await f.read()
        response = await self.server_request(
            path[-1],
            guild_id=path[-4],
            channel_id=path[-3],
            content=content
        )
        if response is None:
            print(f"Invalid request at {event.src_path}")
        else:
            print(f"Handled {path[-1]} at {event.src_path}")

        await aiofiles.os.remove(event.src_path)

    async def start_watchdog(self, guilds: dict[str, list[str]]) -> Awaitable[None]:
        """
        Start watchdog for watching for apis

        :param guilds: Guilds with channels where to watch
        :type guilds: dict[str, list[str]]
        :return: Returns nothing
        :rtype: Awaitable[None]
        """
        for guild in guilds:
            for channel in guilds[guild]:
                self.watchdogs.append(
                    await watch_for(
                        self.path(f"{guild}/{channel}/api/"),
                        self.channel_api_handler
                    )
                )

    async def init(self, data: dict[str, Any]) -> Awaitable[None]:
        """
        Create directories and info files for user, guilds and channels

        :param data: data
        :type data: dict[str, any]
        :return: Returns nothing
        :rtype: Awaitable[None]
        """
        makedirs(
            self.path(""),
            mode=0o755, exist_ok=True
        )

        user = data["user"]
        with open(f"{self.path('')}/info", "w") as f:
            f.write(
                f"ID: {user['id']}\n"
                f"Name: {user['username']}\n"
            )

        guilds: dict[str, list[str]] = {}
        for guild in data["guilds"]:
            guilds[guild["id"]] = []
            makedirs(
                self.path(guild["id"]),
                mode=0o755, exist_ok=True
            )
            with open(f"{self.path(guild['id'])}/info", "w") as f:
                f.write(
                    f"ID: {guild['id']}\n"
                    f"Name: {guild['name']}\n"
                )
            for channel in guild["channels"]:
                if channel["type"] not in (0, 5):
                    continue
                guilds[guild["id"]].append(channel["id"])
                makedirs(
                    self.path(f"{guild['id']}/{channel['id']}/api"),
                    mode=0o755, exist_ok=True
                )
                with open("{}/info".format(self.path(f"{guild['id']}/{channel['id']}")), "w") as f:
                    f.write(
                        f"ID: {channel['id']}\n"
                        f"Name: {channel['name']}\n"
                    )

        await self.start_watchdog(guilds)

    async def message(self, data: dict[str, Any]) -> Awaitable[None]:
        """
        Log message in channel

        :param data: data
        :type data: dict[str, Any]
        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        log_path = self.path(f"{data['guild_id']}/{data['channel_id']}/messages")

        username = data["author"]["username"]
        content = data["content"].split('\n')
        id = data["id"]
        
        before_string = f"{id}/{username}: "

        async with aiofiles.open(log_path, "a") as f:
            await f.write(f"{before_string}{content[0]}\n")
            if len(content) > 1:
                for line in content[1:]:
                    await f.write(f"{' ' * len(before_string)}{line}\n")
