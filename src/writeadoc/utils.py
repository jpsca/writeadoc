import logging
import os
import random
import time
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
from .types import TMetadata


logger = logging.getLogger("writeadoc")
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

META_START = "---"
META_END = "\n---"


def extract_metadata(source: str) -> tuple[str, TMetadata]:
    if not source.startswith(META_START):
        return source, {}

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

    return source.strip().lstrip("- "), meta


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
    print(f"\nServing docs on http://localhost:{port}/")
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


def dict_to_yaml(data: dict, indent: int = 0, is_list_item: bool = False) -> str:
    """Convert a Python dictionary to a YAML string without using external libraries.

    Args:
        data: The dictionary to convert
        indent: Current indentation level (for recursive calls)
        is_list_item: Whether the current item is part of a list

    Returns:
        A formatted YAML string representation
    """
    lines = []
    spaces = " " * indent

    if not data and isinstance(data, dict):
        return "{}" if indent == 0 else "{}"

    for key, value in data.items():
        if isinstance(value, dict):
            if not value:  # Empty dict
                lines.append(f"{spaces}{key}: {{}}")
            else:
                lines.append(f"{spaces}{key}:")
                lines.append(dict_to_yaml(value, indent + 2))
        elif isinstance(value, list):
            if not value:  # Empty list
                lines.append(f"{spaces}{key}: []")
            else:
                lines.append(f"{spaces}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{spaces}  -")
                        lines.append(dict_to_yaml(item, indent + 4, True))
                    else:
                        lines.append(f"{spaces}  - {_format_yaml_value(item)}")
        else:
            prefix = "" if is_list_item else f"{key}: "
            lines.append(f"{spaces}{prefix}{_format_yaml_value(value)}")

    return "\n".join(lines)


def _format_yaml_value(value) -> str:
    """Format a Python value as a YAML value."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if any(char in value for char in ":#{}[],'\"\\"):
            # Quote strings with special characters
            # Escape any existing double quotes
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        return value
    return str(value)


def render_metadata(meta: TMetadata, **kwargs) -> str:
    """Render the metadata as a YAML string without external libraries."""
    meta = {**meta, **kwargs}
    if not meta:
        return ""
    yaml_content = dict_to_yaml(meta)
    return f"---\n{yaml_content}\n---"


