import typing as t
from collections.abc import MutableMapping

import mistune
from mistune.directives import Include, TableOfContents
from mistune.plugins.abbr import abbr
from mistune.plugins.def_list import def_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.task_lists import task_lists

from .admonition import Admonition
from .attrs import block_attrs, inline_attrs
from .block_directive import BlockDirective
from .div import Container
from .figure import Figure
from .formatting import insert, mark, strikethrough, subscript, superscript
from .html_renderer import HTMLRenderer
from .mdjx import mdjx
from .tab import Tab
from .table import table
from .toc import add_toc_hook


md = mistune.Markdown(
    HTMLRenderer(escape=False),
    plugins=[
        # Built-in plugins
        abbr,
        def_list,
        footnotes,
        table,
        task_lists,
        # Custom plugins
        mdjx,
        block_attrs,
        inline_attrs,
        insert,
        mark,
        strikethrough,
        subscript,
        superscript,
        BlockDirective([
            # Built-in directives
            Include(),
            TableOfContents(),
            # Custom directives
            Admonition(),
            Container(),
            Figure(),
            Tab(),
        ]),
    ]
)

add_toc_hook(md)


def render_markdown(source: str, **kwargs: t.Any) -> tuple[str, MutableMapping]:
    """Render the given Markdown source to HTML using the mistune renderer."""
    state = mistune.BlockState()
    state.env.update(kwargs)
    html, state = md.parse(source, state=state)
    return str(html), state.env
