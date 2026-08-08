"""The local server and file watcher behind `writeadoc run`."""

import os
import time
from collections.abc import Callable
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer


__all__ = ("start_server", "start_observer")


def start_server(build_folder: str) -> None:
    """Run a simple HTTP server to serve files from the specified directory."""
    # Create a handler that serves files from build_folder
    port = 8000
    handler = partial(SimpleHTTPRequestHandler, directory=build_folder)
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"Serving docs on http://localhost:{port}/\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def start_observer(
    path, run_callback: Callable, *, path_filter: tuple[str, ...] = ("content", "views")
) -> None:
    """Start a file system observer to watch for changes."""
    event_handler = ChangeHandler(run_callback, path_filter)
    observer = Observer()
    # Watch directory and all subfolders
    observer.schedule(
        event_handler,
        path,
        recursive=True,
        event_filter=[
            FileDeletedEvent,
            FileModifiedEvent,
            FileCreatedEvent,
            FileMovedEvent,
        ],
    )
    observer.start()
    print("Watching for changes. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, run_callback: Callable, path_filter: tuple[str, ...] = ()):
        super().__init__()
        self.run_callback = run_callback
        self.path_filter = path_filter

    def on_any_event(self, event):
        if isinstance(event.src_path, bytes):
            src_path = event.src_path.decode()
        else:
            src_path = str(event.src_path)
        rel_path = os.path.relpath(src_path, os.getcwd())

        if not rel_path.startswith(self.path_filter):
            return

        # Check for file changes in current dir or non-hidden subfolders
        if rel_path.endswith((".py", ".jx", ".md")) and not any(
            part.startswith(".") for part in rel_path.split(os.sep)
        ):
            print(f"File changed ({event.event_type}):", rel_path)
            self.run_callback()
            print("Watching for changes. Press Ctrl+C to exit.")
