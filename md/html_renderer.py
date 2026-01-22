import mistune

from .highlight import HighlightMixin


class HTMLRenderer(
    HighlightMixin,
    mistune.HTMLRenderer
):

    def emphasis(self, text: str) -> str:
        return "<em>" + text + "</em>"

    def strong(self, text: str) -> str:
        return "<strong>" + text + "</strong>"

    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        s = '<a href="' + self.safe_url(url) + '"'
        if title:
            s += ' title="' + safe_entity(title) + '"'
        return s + ">" + text + "</a>"

    def image(self, text: str, url: str, title: Optional[str] = None) -> str:
        src = self.safe_url(url)
        alt = escape_text(striptags(text))
        s = '<img src="' + src + '" alt="' + alt + '"'
        if title:
            s += ' title="' + safe_entity(title) + '"'
        return s + " />"

    def codespan(self, text: str) -> str:
        return "<code>" + escape_text(text) + "</code>"

    def linebreak(self) -> str:
        return "<br />\n"

    def softbreak(self) -> str:
        return "\n"

    def inline_html(self, html: str) -> str:
        if self._escape:
            return escape_text(html)
        return html

    def paragraph(self, text: str) -> str:
        return "<p>" + text + "</p>\n"

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        tag = "h" + str(level)
        html = "<" + tag
        _id = attrs.get("id")
        if _id:
            html += ' id="' + _id + '"'
        return html + ">" + text + "</" + tag + ">\n"

    def blank_line(self) -> str:
        return ""

    def thematic_break(self) -> str:
        return "<hr />\n"

    def block_text(self, text: str) -> str:
        return text

    def block_code(self, code: str, info: Optional[str] = None) -> str:
        html = "<pre><code"
        if info is not None:
            info = safe_entity(info.strip())
        if info:
            lang = info.split(None, 1)[0]
            html += ' class="language-' + lang + '"'
        return html + ">" + escape_text(code) + "</code></pre>\n"

    def block_quote(self, text: str) -> str:
        return "<blockquote>\n" + text + "</blockquote>\n"

    def block_html(self, html: str) -> str:
        if self._escape:
            return "<p>" + escape_text(html.strip()) + "</p>\n"
        return html + "\n"

    def block_error(self, text: str) -> str:
        return '<div class="error"><pre>' + text + "</pre></div>\n"

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        if ordered:
            html = "<ol"
            start = attrs.get("start")
            if start is not None:
                html += ' start="' + str(start) + '"'
            return html + ">\n" + text + "</ol>\n"
        return "<ul>\n" + text + "</ul>\n"

    def list_item(self, text: str) -> str:
        return "<li>" + text + "</li>\n"
