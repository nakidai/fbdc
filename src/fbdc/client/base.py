"""
Abstract class for fbdc clients

BaseClient: abstract class for fbdc clients
"""

from abc import ABC
from typing import Any, Awaitable


class BaseClient(ABC):
    """
    Abstract class for fbdc clients
    """

    async def init(self, data: dict[str, Any]) -> Awaitable[None]:
        """
        Do some preparation when fbdc starts

        :param data: data
        :type data: dict[str, Any]
        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        pass

    async def message(self, data: dict[str, Any]) -> Awaitable[None]:
        """
        Process message (print, write to log, print on paper etc)

        :param data: data
        :type data: dict[str, Any]
        :return: Returns nothing
        :rtype: Awaitable[None]
        """

        pass
