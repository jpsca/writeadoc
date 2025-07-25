import os
import re
import typing as t

from watchdog.events import FileSystemEventHandler
import yaml
from pymdownx import emoji

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader  # type: ignore

from .exceptions import InvalidFrontMatter


DEFAULT_MD_EXTENSIONS = [
    "attr_list",
    "def_list",
    "md_in_html",
    "meta",
    "sane_lists",
    "tables",
    "pymdownx.betterem",
    "pymdownx.blocks.admonition",
    "pymdownx.caret",
    "pymdownx.emoji",
    "pymdownx.highlight",
    "pymdownx.inlinehilite",
    "pymdownx.magiclink",
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
    "pymdownx.highlight": {
        "linenums_style": "pymdownx-inline",
        "anchor_linenums": False,
        "css_class": "highlight",
        "linenums": True,
        "pygments_lang_class": True,
    },
    "pymdownx.superfences": {
        "disable_indented_code_blocks": True,
    },
    "pymdownx.emoji": {
        "emoji_generator": emoji.to_alt,
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



RX_ABS_URL = re.compile(
    r"""(\s(?:src|href|action|data-[a-z0-9_-]+)\s*=\s*['"])(\/(?:[a-z0-9_-][^'"]*)?)(['"])""",
    re.IGNORECASE,
)

def relativize_urls(html: str, current_url: str) -> str:
    depth = current_url.lstrip("/").count("/")
    pos = 0
    while True:
        match = RX_ABS_URL.search(html, pos=pos)
        if not match:
            break
        left, url, right = match.groups()
        new_url = relativize_url(url, depth)
        pos = match.end()
        html = f"{html[: match.start()]}{left}{new_url}{right}{html[pos:]}"

    return html


def relativize_url(url: str, depth: int) -> str:
    new_url = f'{"../" * depth}{url.lstrip("/")}'
    if not new_url.startswith("."):
        new_url = f"./{new_url}"
    if new_url.endswith("/"):
        new_url = f"{new_url}index.html"
    return new_url


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
