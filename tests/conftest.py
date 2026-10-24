import functools
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from playwright.sync_api import expect

APP_DIR = Path(__file__).resolve().parents[1] / "app"
PORT = 8080


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return


class _Server(ThreadingHTTPServer):
    allow_reuse_address = True


class _ServerV6(_Server):
    address_family = socket.AF_INET6


def _start_server(server_cls, host):
    handler = functools.partial(_QuietHandler, directory=str(APP_DIR))
    httpd = server_cls((host, PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


@pytest.fixture(scope="session", autouse=True)
def app_server():
    """Serve the unmodified assessment app at http://localhost:8080."""
    required = ("index.html", "vf-container.html", "app.html")
    missing = [name for name in required if not (APP_DIR / name).is_file()]
    if missing:
        raise RuntimeError(
            f"Place the assessment files in {APP_DIR}: {', '.join(missing)}"
        )

    expect.set_options(timeout=20_000)
    servers = [_start_server(_Server, "127.0.0.1")]
    try:
        servers.append(_start_server(_ServerV6, "::1"))
    except OSError:
        pass

    try:
        yield
    finally:
        for httpd in servers:
            httpd.shutdown()
            httpd.server_close()
