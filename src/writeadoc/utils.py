import logging
import os
import time
import typing as t
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader  # type: ignore

from .exceptions import InvalidFrontMatter


logger = logging.getLogger("writeadoc")

DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "md_in_html",
    "tables",
    "toc",
    "pymdownx.betterem",
    "pymdownx.blocks.admonition",
    "pymdownx.blocks.details",
    "pymdownx.caret",
    "pymdownx.fancylists",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.mark",
    "pymdownx.saneheaders",
    "pymdownx.smartsymbols",
    "pymdownx.superfences",
    "pymdownx.tasklist",
    "pymdownx.tilde",
]

DEFAULT_MD_CONFIG = {
    "keys": {
        "camel_case": True,
    },
    "toc": {
        "permalink": True,
        "permalink_title": "",
        "toc_depth": 3,
    },
    "pymdownx.blocks.admonition": {
        "types": [
            "note",
            "tip",
            "warning",
            "danger",
            "new",
            "question",
            "error",
            "example",
        ],
    },
    "pymdownx.fancylists": {
        "additional_ordered_styles": ["roman", "alpha", "generic"],
        "inject_class": True,
    },
    "pymdownx.highlight": {
        "linenums_style": "pymdownx-inline",
        "anchor_linenums": False,
        "css_class": "highlight",
        "pygments_lang_class": True,
    },
    "pymdownx.superfences": {
        "disable_indented_code_blocks": True,
    },
}

TMetadata = dict[str, t.Any]
META_START = "---"
META_END = "\n---"


def extract_metadata(source: str) -> tuple[TMetadata, str]:
    if not source.startswith(META_START):
        return {}, source

    source = source.strip().lstrip("- ")
    front_matter, source = source.split(META_END, 1)
    try:
        meta = yaml.load(front_matter, SafeLoader)
    except Exception as err:
        raise InvalidFrontMatter(truncate(source), *err.args)

    return meta, source.strip().lstrip("- ")


def truncate(source: str) -> str:
    if len(source) > 203:
        return f"{source[:200]}..."
    return source


def start_server(build_folder: str) -> None:
    """Run a simple HTTP server to serve files from the specified directory."""
    # Create a handler that serves files from build_folder
    port = 8000
    handler = partial(SimpleHTTPRequestHandler, directory=build_folder)
    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    url = f"http://localhost:{port}/"
    print(f"Serving docs on {url}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def start_observer(path, run_callback) -> None:
    """Start a file system observer to watch for changes."""
    event_handler = ChangeHandler(run_callback)
    observer = Observer()
    # Watch directory and all subfolders
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("Watching for changes. Press Ctrl+C to exit.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, run_callback):
        super().__init__()
        self.run_callback = run_callback

    def on_any_event(self, event):
        # Only act on file changes (not directory events)
        if event.is_directory or event.event_type in ("opened", "closed", "closed_no_write"):
            return
        if isinstance(event.src_path, bytes):
            src_path = event.src_path.decode()
        else:
            src_path = str(event.src_path)
        rel_path = os.path.relpath(src_path, os.getcwd())

        if rel_path.startswith("build" + os.sep) or rel_path.startswith("."):
            return

        # Check for file changes in current dir or non-hidden subfolders
        if (
            rel_path.endswith((".py", ".jinja", ".md"))
            and not any(part.startswith(".") for part in rel_path.split(os.sep))
        ):
            print(f"File changed ({event.event_type}):", rel_path)
            self.run_callback()
            print("Watching for changes. Press Ctrl+C to exit.\n")
