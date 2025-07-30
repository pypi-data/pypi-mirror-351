from dataclasses import dataclass
from typing import NotRequired, TypedDict


class VueSSRConfig(TypedDict):
    """
    Helper type to configure Vue SSR in settings.py.

    Example:
        VUE_SSR: VueSSRConfig = {
            "host": "localhost",
            "port": 3123,
        }
    """

    host: NotRequired[str]
    """ Host for Vue SSR server. Defaults to `localhost`. """
    port: NotRequired[str | int]
    """ Port for Vue SSR server. Defaults to `3123`. """
    socket: NotRequired[str | None]
    """ Unix socket path for Vue SSR server. """
    protocol: NotRequired[str]
    """ Protocol for Vue SSR server. Defaults to `http`. """
    vite_host: NotRequired[str]
    """ Host for Vite server during development. Defaults to `localhost`. """
    vite_port: NotRequired[str]
    """ Port for Vite server during development. Defaults to `5173`. """
    vite_protocol: NotRequired[str]
    """ Protocol for Vite server during development. Defaults to `http`. """
    timeout: NotRequired[int | None]
    """ Timeout for Vue SSR requests in milliseconds (default: 10). Set to None to disable timeout. """
    debug: NotRequired[bool]
    """Enable debug mode for Vue SSR. In debug mode, Vite will be used to render components. Defaults to `settings.DEBUG`."""


@dataclass(frozen=True)
class VueSSRSettings:
    """
    @private
    """

    host: str
    port: str | int
    socket: str | None
    protocol: str
    vite_host: str
    vite_port: str
    vite_protocol: str
    timeout: int
    debug: bool


def get_vue_ssr_settings() -> VueSSRSettings:
    """
    @private
    Get the Vue SSR settings.
    :return: VueSSRSettings
    """
    from django.conf import settings

    config: VueSSRConfig = getattr(settings, "VUE_SSR", VueSSRConfig())

    return VueSSRSettings(
        host=config.get("host", "127.0.0.1"),
        port=config.get("port", "3123"),
        socket=config.get("socket"),
        protocol=config.get("protocol", "http"),
        vite_host=config.get("vite_host", ""),
        vite_port=config.get("vite_port", ""),
        vite_protocol=config.get("vite_protocol", "http"),
        timeout=config.get("timeout") or 10,
        debug=config.get("debug", settings.DEBUG),
    )
