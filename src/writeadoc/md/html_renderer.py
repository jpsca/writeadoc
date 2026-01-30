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

    def link(self, text: str, url: str, title: str | None = None, **attrs: t.Any) -> str:
        attrs["href"] = url
        if title:
            attrs["title"] = title
        return f"<a{render_attrs(attrs)}>{text}</a>"

    def image(self, text: str, url: str, title: str | None = None, **attrs: t.Any) -> str:
        attrs["src"] = url
        attrs["alt"] = escape(striptags(text))
        if title:
            attrs["title"] = title
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
        # The attributes are not parsed for block quotes, but we allow them
        # to be passed and rendered for future compatibility.
        return f"<blockquote{render_attrs(attrs)}>{text}</blockquote>\n"

    def list(self, text: str, ordered: bool, **attrs: t.Any) -> str:
        # The attributes are not parsed for lists, but we allow them
        # to be passed and rendered for future compatibility.
        if ordered:
            return f"<ol{render_attrs(attrs)}>\n{text}</ol>\n"
        return f"<ul{render_attrs(attrs)}>\n{text}</ul>\n"

    def list_item(self, text: str, **attrs: t.Any) -> str:
        # The attributes are not parsed for list items, but we allow them
        # to be passed and rendered for future compatibility.
        return f"<li{render_attrs(attrs)}>{text}</li>\n"

    # For the methods below, allow attributes
    # (possible with syntax errors) but ignore them

    def text(self, text: str, **attrs: t.Any) -> str:
        return super().text(text)

    def linebreak(self, **attrs: t.Any) -> str:
        return "<br />\n"

    def softbreak(self, **attrs: t.Any) -> str:
        return "\n"

    def inline_html(self, html: str, **attrs: t.Any) -> str:
        return super().inline_html(html)

    def block_html(self, html: str, **attrs: t.Any) -> str:
        return super().block_html(html)

    def blank_line(self, **attrs: t.Any) -> str:
        return ""

    def block_text(self, text: str, **attrs: t.Any) -> str:
        return text
