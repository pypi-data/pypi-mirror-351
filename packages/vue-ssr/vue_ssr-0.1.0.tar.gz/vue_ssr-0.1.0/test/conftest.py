import os
import subprocess
from pathlib import Path

import pytest
from django.conf import settings

from vue_ssr.services import setup_renderer


@pytest.fixture()
def production():
    """
    Fixture to set the production environment.
    """
    settings.DEBUG = False
    setup_renderer()
    yield


@pytest.fixture()
def development():
    """
    Fixture to set the development environment.
    """
    settings.DEBUG = True
    setup_renderer()
    yield


class ViteDevServer:
    """
    A class to start and stop the Vite dev server.
    """

    process = None

    def __init__(self, cwd=settings.FRONTEND_DIR, port=5173):
        self.cwd = cwd
        self.port = str(port)

    def start(self):
        """
        Start the Vite dev server.
        """

        self.process = subprocess.Popen(
            ["pnpm", "run", "dev", "--port", self.port],
            cwd=self.cwd,
            stdout=subprocess.PIPE,
        )

        while True:
            line = self.process.stdout.readline()
            if b"ready" in line:
                break

    def stop(self):
        """
        Stop the Vite dev server.
        """
        if self.process:
            self.process.terminate()
            self.process.wait()


class VueSSRServer:
    """
    A class to start and stop the Vite dev server.
    """

    process = None

    def __init__(
        self,
        manifest: str,
        command: list[str],
        cwd=settings.FRONTEND_DIR,
        port=22634,
        socket: str | None = None,
    ):
        self.manifest = manifest
        self.cwd = cwd
        self.port = str(port)
        self.socket = socket
        self.command = command

    def start(self):
        """
        Start the Vite dev server.
        """

        args = list(self.command)

        if self.socket:
            args += ["--socket", self.socket]
        else:
            args += ["--port", self.port, "--host", "localhost"]

        args += [self.manifest]

        self.process = subprocess.Popen(
            args,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
        )

        while True:
            line = self.process.stdout.readline()
            if line:
                print(line)
            if b"Server running" in line:
                print("Vue SSR server started")
                break

    def stop(self):
        """
        Stop the Vite dev server.
        """
        if self.process:
            self.process.terminate()
            self.process.wait()


@pytest.fixture()
def vite_dev_server():
    """
    Fixture to start and stop the Vite dev server.
    """
    server = ViteDevServer()
    server.start()
    yield server
    server.stop()


COMMANDS = [["pnpm", "exec", "vue-ssr-service"], ["bun", "run", "vue-ssr-service"]]


@pytest.fixture(params=COMMANDS)
def vue_ssr_server(request):
    """
    Fixture to start and stop the Vue SSR server.
    """
    server = VueSSRServer(
        str(settings.FRONTEND_DIR / "dist" / "server" / "manifest.json"),
        command=request.param,
    )
    server.start()
    yield server
    server.stop()


@pytest.fixture(params=COMMANDS)
def vue_ssr_socket_server(request):
    """
    Fixture to start and stop the Vue SSR server with a socket.
    """
    runtime = request.param[0]
    socket = str(Path(f"test-socket-{runtime}.sock").resolve())
    server = VueSSRServer(
        str(settings.FRONTEND_DIR / "dist" / "server" / "manifest.json"),
        command=request.param,
        socket=socket,
    )
    server.start()
    yield server, socket
    server.stop()
    os.remove(socket)
