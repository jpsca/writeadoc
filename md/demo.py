import mistune
from mistune.directives import FencedDirective, TableOfContents
from mistune.plugins.abbr import abbr
from mistune.plugins.def_list import def_list
from mistune.plugins.footnotes import footnotes
from mistune.plugins.formatting import insert, mark, strikethrough, subscript, superscript
from mistune.plugins.table import table
from mistune.plugins.task_lists import task_lists
from mistune.renderers.markdown import MarkdownRenderer

from .admonition import Admonition
from .attrs import inline_attrs
from .html_renderer import HTMLRenderer


source = ("""\
Hello World.

For instance, [TypLog](https://typlog.com/){ target="_blank" }

Bye.
""")


markdown = mistune.Markdown(
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
            TableOfContents(),
            # Tab(),
        ]),
    ]
)

md_renderer = MarkdownRenderer()
print(markdown(source))
