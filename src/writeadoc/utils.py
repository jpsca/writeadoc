import logging
import os
import random
import time
import typing as t
from collections.abc import Callable
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import strictyaml
from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from .exceptions import InvalidFrontMatter


logger = logging.getLogger("writeadoc")

DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "md_in_html",
    "tables",
    "writeadoc.pagetoc",
    "writeadoc.tab",
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
    "writeadoc.pagetoc": {
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
        data = strictyaml.load(front_matter).data
        if isinstance(data, dict):
            meta = {**data}
        else:
            meta = {}
    except Exception as err:
        raise InvalidFrontMatter(truncate(source), *err.args) from err

    return meta, source.strip().lstrip("- ")


def truncate(source: str, limit: int = 400) -> str:
    if len(source) > limit:
        return f"{source[: limit - 3]}..."
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
    print("\nWatching for changes. Press Ctrl+C to exit.")
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
        if rel_path.endswith((".py", ".jinja", ".md")) and not any(
            part.startswith(".") for part in rel_path.split(os.sep)
        ):
            print(f"File changed ({event.event_type}):", rel_path)
            self.run_callback()
            print("Watching for changes. Press Ctrl+C to exit.")


RANDOM_MESSAGES = [
    "Accessing hidden memories",
    "Activating hyperdrive",
    "Activating unknown hardware",
    "Adjusting the dilithium crystals",
    "Aligning the stars",
    "Bending the event horizon",
    "Bending the spoon",
    "Brewing fresh markdown",
    "Calibrating the flux capacitor",
    "Challenging everything",
    "Chasing Schrödinger's cat",
    "Counting to 42 backwards",
    "Debating documentation as art",
    "Deciphering the matrix",
    "Decrypting nuclear codes",
    "Deterministically simulating the future",
    "Distilling beauty",
    "Distilling delight",
    "Distilling enjoyment",
    "Embedding code blocks",
    "Exceeding CPU quota",
    "Extracting meaning",
    "Filtering the ozone",
    "Fixing the ozone layer",
    "Folding sections with care",
    "Formatting with finesse",
    "Iodizing",
    "Liquefying bytes",
    "Lowering the entropy",
    "Mixing metadata magic",
    "Optimizing for happiness",
    "Polishing the pixels",
    "Processing every third letter",
    "Refactoring the universe",
    "Rendering emotional depth",
    "Rendering inspiration",
    "Reversing the bits polarity",
    "Revolving independence",
    "Reversing global warming",
    "Sandbagging expectations",
    "Self affirming",
    "Shaking",
    "Sifting through syntax",
    "Summoning the muses",
    "Swapping time and space",
    "Testing CO2 levels",
    "Tokenizing innovation",
]



def get_random_messages(num: int = 3) -> list[str]:
    return random.sample(RANDOM_MESSAGES, min(num, len(RANDOM_MESSAGES)))


