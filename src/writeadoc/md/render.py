import re
import typing as t
import unicodedata
from collections.abc import MutableMapping

import mistune
from mistune.directives import FencedDirective, Include, TableOfContents
from mistune.plugins.abbr import abbr
from mistune.plugins.def_list import def_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.formatting import insert, mark, strikethrough, subscript, superscript
from mistune.plugins.table import table
from mistune.plugins.task_lists import task_lists
from mistune.toc import add_toc_hook

from .admonition import Admonition
from .attrs import inline_attrs
from .html_renderer import HTMLRenderer


md = mistune.Markdown(
    HTMLRenderer(),
    plugins=[
        abbr,
        def_list,
        footnotes,
        insert,
        mark,
        strikethrough,
        subscript,
        superscript,
        table,
        task_lists,
        inline_attrs,
        # md_in_html, ???
        FencedDirective([
            Admonition(),
            Include(),
            TableOfContents(),
            # Tab(),
        ]),
    ]
)


def slugify(value: str, separator: str = "-", unicode: bool = True) -> str:
    """Slugify a string, to make it URL friendly."""
    if not unicode:
        # Replace Extended Latin characters with ASCII, i.e. `žlutý` => `zluty`
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[{}\s]+".format(separator), separator, value)


def heading_id(token: dict[str, t.Any], index: int) -> str:
    return slugify(token["text"])


add_toc_hook(md, heading_id=heading_id)


def render_markdown(source: str) -> tuple[str, MutableMapping]:
    """Render the given Markdown source to HTML using the mistune renderer."""
    html, state = md.parse(source)
    return str(html), state.env
