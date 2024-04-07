from typing import Any, Callable, Awaitable
from functools import partial
import asyncio
import json

from .client import Client

import websockets
import requests


class Server:
    def __init__(self, token: str, client: Client) -> None:
        self.token: str = token
        self.client: Client = client
        self.client.server_request = self.client_request

        self.socket: websockets.WebSocketClientProtocol | None = None
        self.heartbeat_interval: float | None = None
        self.sequence: str | None = None

    async def client_request(self, type, **kwargs) -> Any:
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
        await self.socket.send(json.dumps(request))

    async def get_request(self) -> Awaitable[dict[str, Any]]:
        response: str | None = await self.socket.recv()
        return json.loads(response) if response else None
    
    async def send_api_request(self, type: str, path: str, request: dict[str, Any] = {}) -> Awaitable[requests.Response]:
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
        await self.send_request({"op": 1, "d": self.sequence})

    async def heartbeat(self) -> Awaitable[None]:
        await asyncio.sleep(self.heartbeat_interval)
        while self.socket.open:
            await self.heartbeat_send()
            await asyncio.sleep(self.heartbeat_interval)

    async def loop(self) -> Awaitable[None]:
        while True:
            response = await self.get_request()
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

    async def socket_run(self) -> Awaitable[None]:
        async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as socket:
            self.socket = socket
            self.heartbeat_interval = (await self.get_request())["d"]["heartbeat_interval"] / 1000

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

    def start(self) -> None:
        try:
            asyncio.run(self.socket_run())
        except KeyboardInterrupt:
            pass
