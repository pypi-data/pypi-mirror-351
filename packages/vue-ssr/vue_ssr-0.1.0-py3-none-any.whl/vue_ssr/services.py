import logging
from typing import Any

import requests

from .settings import get_vue_ssr_settings
from .vue_ssr import ServerRenderer, SocketServerRenderer, SSRRenderer, ViteRenderer

logger = logging.getLogger(__name__)

renderer: SSRRenderer
timeout: int
dev_mode = False


def setup_renderer():
    global renderer, timeout, dev_mode

    settings = get_vue_ssr_settings()

    timeout = settings.timeout
    dev_mode = settings.debug

    if settings.debug:
        vite_host = settings.vite_host or "localhost"
        vite_port = settings.vite_port or 5173
        vite_proto = settings.vite_protocol or "http"

        if not settings.vite_host or not settings.vite_port:
            try:
                from django_vite.core.asset_loader import (
                    DEFAULT_APP_NAME,
                    DjangoViteAssetLoader,
                )

                instance = DjangoViteAssetLoader.instance()
                app = instance._get_app_client(DEFAULT_APP_NAME)

                vite_host = app.dev_server_host
                vite_port = app.dev_server_port
                vite_proto = app.dev_server_protocol
            except ImportError:
                pass

        renderer = ViteRenderer(host=vite_host, port=vite_port, protocol=vite_proto)
    elif settings.socket:
        renderer = SocketServerRenderer(socket=settings.socket)
    else:
        kwargs = {
            "host": settings.host,
            "port": settings.port,
            "protocol": settings.protocol,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        renderer = ServerRenderer(**kwargs)


def render(entry: str, props: dict[str, Any] = {}) -> str | None:
    """
    Render the given entry with the provided props.
    :param entry: The path to the SSR entry.
    :param props: The props passed to the entry.
    :return: The rendered HTML.
    """

    try:
        return renderer.render(entry, props, timeout=timeout)
    except Exception as e:
        if dev_mode:
            if isinstance(e, requests.exceptions.ConnectionError):
                raise Exception(
                    "Could not connect to Vue SSR service. Is it running?"
                ) from e
            else:
                raise Exception(f"Could not render {entry}.") from e

        logger.error(f'Could not render "{entry}"', exc_info=e)
        return None
