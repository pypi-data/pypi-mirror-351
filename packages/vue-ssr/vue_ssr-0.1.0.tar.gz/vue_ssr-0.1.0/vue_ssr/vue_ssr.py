from abc import ABC, abstractmethod
from functools import cached_property
from os import PathLike
from typing import Any, Optional
from urllib.parse import quote

import requests
import requests_unixsocket


class SSRRenderer(ABC):
    """Abstract base class for SSR renderers."""

    @abstractmethod
    def render(
        self,
        entry: str,
        props: dict[str, Any] = {},
        timeout: float | None = None,
    ) -> str:
        pass


class ServerRenderer(SSRRenderer):
    """Connect to a vue-ssr-service server via HTTP."""

    host: Optional[str]
    port: Optional[str]
    protocol: Optional[str]

    _session: requests.Session

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: str | int = 3123,
        protocol: str = "http",
    ):
        """
        :param host: The server host.
        :param port: The server port.
        :param protocol: The protocol (http or https).
        """

        self._session = requests.Session()
        self.host = host
        self.port = str(port)
        self.protocol = protocol

    @cached_property
    def address(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"

    def render(
        self,
        entry: str,
        props: dict[str, Any] = {},
        timeout: float | None = None,
    ) -> str:
        """
        Render the given entry with the provided props.
        :param entry: The name of the SSR entry.
        :param props: The props passed to the entry.
        :return: The rendered HTML.
        """
        url = f"{self.address}/render"
        data = {"entryName": entry, "props": props}
        response = self._session.post(url, json=data, timeout=timeout)

        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"SSR error: {response.status_code} - {response.text}")


class SocketServerRenderer(ServerRenderer):
    """Connect to a vue-ssr-service server via a UNIX socket."""

    def __init__(self, socket: PathLike | str):
        """
        :param socket: The path to the Unix socket.
        """
        self.unix_socket = str(socket)
        self._session = requests_unixsocket.Session()

    @cached_property
    def address(self) -> str:
        return f"http+unix://{quote(self.unix_socket, safe='')}"


class ViteRenderer(SSRRenderer):
    """Connect to a Vite dev server via HTTP."""

    host: str
    port: str
    protocol: str

    _session = requests.Session()

    def __init__(
        self, host: str = "127.0.0.1", port: int | str = "5173", protocol: str = "http"
    ) -> None:
        """
        :param host: The Vite dev server host.
        :param port: The Vite dev server port.
        :param protocol: The protocol (http or https).
        """
        self.host = host
        self.port = str(port)
        self.protocol = protocol

    @cached_property
    def address(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"

    def render(
        self,
        entry: str,
        props: dict[str, Any] = {},
        timeout: float | None = None,
    ) -> str:
        """
        Render the given entry with the provided props.
        :param entry: The name of the SSR entry.
        :param props: The props passed to the entry.
        :return: The rendered HTML.
        """
        url = f"{self.address}/__vue-ssr"
        data = {"entryName": entry, "props": props}
        response = self._session.post(url, json=data, timeout=timeout)

        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"SSR error: {response.status_code} - {response.text}")
