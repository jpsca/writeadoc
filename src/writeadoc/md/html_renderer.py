import typing as t

import mistune
from mistune.util import escape, striptags

from .highlight import HighlightMixin
from .utils import render_attrs


class HTMLRenderer(HighlightMixin, mistune.HTMLRenderer):

    def emphasis(self, text: str, **attrs: t.Any) -> str:
        return f"<em{render_attrs(attrs)}>{text}</em>"

    def strong(self, text: str, **attrs: t.Any) -> str:
        return f"<strong{render_attrs(attrs)}>{text}</strong>"

    def link(self, text: str, **attrs: t.Any) -> str:
        return f"<a{render_attrs(attrs)}>{text}</a>"

    def image(self, text: str, **attrs: t.Any) -> str:
        attrs["alt"] = escape(striptags(text))
        return f"<img{render_attrs(attrs)} />"

    def codespan(self, text: str, **attrs: t.Any) -> str:
        return f"<code{render_attrs(attrs)}>{escape(text)}</code>"

    def paragraph(self, text: str, **attrs: t.Any) -> str:
        return f"<p{render_attrs(attrs)}>{text}</p>\n"

    def heading(self, text: str, level: int, **attrs: t.Any) -> str:
        return f"<h{level}{render_attrs(attrs)}>{text}</h{level}>\n"

    def thematic_break(self, **attrs: t.Any) -> str:
        return f"<hr{render_attrs(attrs)}/>\n"

    def block_quote(self, text: str, **attrs: t.Any) -> str:
        return f"<blockquote{render_attrs(attrs)}>{text}</blockquote>\n"

    def list(self, text: str, ordered: bool, **attrs: t.Any) -> str:
        if ordered:
            return f"<ol{render_attrs(attrs)}>\n{text}</ol>\n"
        return f"<ul{render_attrs(attrs)}>\n{text}</ul>\n"

    def list_item(self, text: str, **attrs: t.Any) -> str:
        return f"<li{render_attrs(attrs)}>{text}</li>\n"
