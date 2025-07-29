"""Rebuild Basicest site on changes, with hot reloading in the browser."""

from __future__ import annotations

import argparse
import shlex
import sys
import tempfile
from pathlib import Path

import colorama
import uvicorn

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from .build import Builder
from .filter import IgnoreFilter
from .middleware import JavascriptInjectorMiddleware
from .server import RebuildServer
from .utils import find_free_port, open_browser, show_message


def main(argv=()):
    """Actual application logic."""
    colorama.just_fix_windows_console()

    if not argv:
        # entry point functions don't receive args
        argv = sys.argv[1:]

    args, build_args = _parse_args(list(argv))
    with tempfile.TemporaryDirectory() as out_temp_dir:
        src_dir = args.root
        out_dir = Path(out_temp_dir)

        serve_dir = out_dir

        host_name = args.host
        port_num = args.port or find_free_port()
        url_host = f"{host_name}:{port_num}"


        builder = Builder(
            ["--out", str(out_dir), str(args.root)] + build_args,
            url_host=url_host,
        )

        watch_dirs = [src_dir] + args.additional_watched_dirs

        app = _create_app(watch_dirs, builder, serve_dir, url_host)

        show_message("Starting initial build")
        builder(changed_paths=())

        if args.open_browser:
            open_browser(url_host, args.delay)

        show_message("Waiting to detect changes...")
        try:
            uvicorn.run(app, host=host_name, port=port_num, log_level="warning")
        except KeyboardInterrupt:
            show_message("Server ceasing operations. Cheerio!")


def _create_app(watch_dirs, builder, out_dir, url_host):
    watcher = RebuildServer(watch_dirs, (lambda _: False), change_callback=builder)

    return Starlette(
        routes=[
            WebSocketRoute("/websocket-reload", watcher, name="reload"),
            Mount("/", app=StaticFiles(directory=out_dir, html=True), name="static"),
        ],
        middleware=[Middleware(JavascriptInjectorMiddleware, ws_url=url_host)],
        lifespan=watcher.lifespan,
    )


def _parse_args(argv):
    parser = _get_parser()
    args, build_args = parser.parse_known_args(argv.copy())
    return args, build_args


def _get_parser():
    """Get the application's argument parser."""
    parser = argparse.ArgumentParser(allow_abbrev=False)
    _add_autobuild_arguments(parser)

    return parser


def _add_autobuild_arguments(parser):
    group = parser.add_argument_group("autobuild options")
    group.add_argument(
        "--port",
        type=int,
        default=0,
        help="port to serve documentation on. 0 means find and use a free port",
    )
    group.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="hostname to serve documentation on",
    )
    group.add_argument(
        "--open-browser",
        action="store_true",
        default=False,
        help="open the browser after building documentation",
    )
    group.add_argument(
        "--delay",
        dest="delay",
        type=float,
        default=5,
        help="how long to wait before opening the browser",
    )
    group.add_argument(
        "--watch",
        action="append",
        metavar="DIR",
        default=[],
        type=Path,
        help="additional directories to watch",
        dest="additional_watched_dirs",
    )
    parser.add_argument("root", help="Project root directory", type=Path)
    return group


if __name__ == "__main__":
    main(sys.argv[1:])
