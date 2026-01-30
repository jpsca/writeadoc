import re
import typing as t
import unicodedata
from collections.abc import MutableMapping

import mistune
from mistune.directives import Include, TableOfContents
from mistune.plugins.abbr import abbr
from mistune.plugins.def_list import def_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.table import table
from mistune.plugins.task_lists import task_lists
from mistune.toc import add_toc_hook

from .admonition import Admonition
from .attrs import block_attrs, inline_attrs
from .block_directive import BlockDirective
from .div import Container
from .figure import Figure
from .formatting import insert, mark, strikethrough, subscript, superscript
from .html_renderer import HTMLRenderer
from .tab import Tab


md = mistune.Markdown(
    HTMLRenderer(escape=False),
    plugins=[
        abbr,
        def_list,
        footnotes,
        table,
        task_lists,
        #
        block_attrs,
        inline_attrs,
        insert,
        mark,
        strikethrough,
        subscript,
        superscript,
        # md_in_html, ???
        BlockDirective([
            Include(),
            TableOfContents(),
            #
            Admonition(),
            Container(),
            Figure(),
            Tab(),
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


def render_markdown(source: str, **kwargs: t.Any) -> tuple[str, MutableMapping]:
    """Render the given Markdown source to HTML using the mistune renderer."""
    state = mistune.BlockState()
    state.env.update(kwargs)
    html, state = md.parse(source, state=state)
    return str(html), state.env
