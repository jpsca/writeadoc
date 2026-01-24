from collections.abc import MutableMapping

import mistune
from mistune.directives import FencedDirective, TableOfContents
from mistune.plugins.abbr import abbr
from mistune.plugins.def_list import def_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.formatting import insert, mark, strikethrough, subscript, superscript
from mistune.plugins.table import table
from mistune.plugins.task_lists import task_lists
from mistune.toc import add_toc_hook

from .admonition import Admonition
from .attrs import attrs_list
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
        attrs_list,
        # md_in_html, ???
        FencedDirective([
            Admonition(),
            TableOfContents(),
            # Tab(),
        ]),
    ]
)
add_toc_hook(md)


def render_markdown(source: str) -> tuple[str, MutableMapping]:
    """Render the given Markdown source to HTML using the mistune renderer."""
    html, state = md.parse(source)
    return str(html), state.env
