"""
This module contains discord server

Server(token: str, client: fbdc.client.BaseClient): server which talks with discord
"""


import asyncio
import json
from functools import partial
from typing import Any, Awaitable, Callable, Never

import requests
import websockets

from .client import BaseClient


class Server:
    """Server which talks with discord"""

    def __init__(self, token: str, client: BaseClient) -> None:
        """
        Server which talks with discord

        :param token: User's token
        :type token: str
        :param client: Client for interacting with user
        :type client: BaseClient
        """

        if not isinstance(client, BaseClient):
            raise TypeError("Client should be inherited from fbdc.client.BaseClient")

        self.token: str = token
        self.client: BaseClient = client
        self.client.server_request = self.client_request

        self.socket: websockets.WebSocketClientProtocol | None = None
        self.heartbeat_interval: float | None = None
        self.sequence: str | None = None

    async def client_request(self, type: str, **kwargs) -> Any:
        """
        Handle client's requests

        :param type: type of the request
        :type type: str
        :param kwargs: request arguments
        :return: Returns return from requested or None on invalid type
        :rtype: Any
        """

        match type:
            case "message_send":
                return await self.send_api_request(
                    "POST",
                    f"channels/{kwargs['channel_id']}/messages",
                    {
                        "content": kwargs["content"]
                    }
                )
            case _:
                return None

    async def send_request(self, request: dict[str, Any]) -> Awaitable[None]:
        """
        Send request to the websocket

        :param request: request's data
        :type request: dict[str, Any]
        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        await self.socket.send(json.dumps(request))

    async def get_response(self) -> Awaitable[dict[str, Any]]:
        """
        Get response from the websocket

        :return: Returns response
        :rtype: Awaitable[dict[str, Any]]
        """

        response: str | None = await self.socket.recv()
        return json.loads(response) if response else None
    
    async def send_api_request(self, type: str, path: str, request: dict[str, Any] = {}) -> Awaitable[requests.Response]:
        """
        Send request to the api

        :param type: Type of request, either "POST" or "GET"
        :type type: str
        :param path: path to the request
        :type path: str
        :param request: request's data
        :type request: dict[str, Any]
        :return: Returns response from the discord's api
        :rtype: Awaitable[requests.Response]
        """

        loop = asyncio.get_running_loop()

        match type:
            case "POST":
                return await loop.run_in_executor(
                    None,
                    partial(
                        requests.post,
                        url=f"https://discord.com/api/v9/{path}",
                        headers={
                            "Authorization": self.token
                        },
                        json=request
                    )
                )
            case "GET":
                return await loop.run_in_executor(
                    None,
                    partial(
                        requests.get,
                        url=f"https://discord.com/api/v9/{path}",
                        headers={
                            "Authorization": self.token
                        },
                        json=request
                    )
                )

    async def heartbeat_send(self) -> Awaitable[None]:
        """
        Send heartbeat

        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        await self.send_request({"op": 1, "d": self.sequence})

    async def heartbeat(self) -> Awaitable[None]:
        """
        Send heartbeat and wait interval got from the first response

        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        await asyncio.sleep(self.heartbeat_interval)
        while self.socket.open:
            await self.heartbeat_send()
            await asyncio.sleep(self.heartbeat_interval)

    async def loop(self) -> Awaitable[Never]:
        """Process requests from websocket in a loop"""
        while True:
            response = await self.get_response()
            self.sequence = response["s"]

            if response["op"] == 1:
                await self.heartbeat
                continue

            match response["t"]:
                case "READY":
                    await self.client.init(response["d"])
                    print("Ready")
                case "MESSAGE_CREATE":
                    if response["d"].get("guild_id") is None:
                        continue
                    await self.client.message(response["d"])

    async def socket_run(self) -> Awaitable[Never]:
        """Connect to the websocket and start heartbeat loop with main loop"""

        async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as socket:
            self.socket = socket
            self.heartbeat_interval = (await self.get_response())["d"]["heartbeat_interval"] / 1000

            await self.send_request(
                {
                    "op": 2,
                    "d":
                    {
                        "token": self.token,
                        "properties":
                        {
                            "os": "Windows 11",
                            "browser": "Google Chrome",
                            "device": "Windows"
                        }
                    }
                }
            )

            await asyncio.gather(
                self.heartbeat(),
                self.loop()
            )

    def start(self) -> Never:
        """Convenient wrapper for Server.socket_run"""

        try:
            asyncio.run(self.socket_run())
        except KeyboardInterrupt:
            pass


__all__ = ["Server"]
