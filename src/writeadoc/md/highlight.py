import re
import typing as t
from collections.abc import Callable

import mistune
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name


class CustomHtmlFormatter(HtmlFormatter):
    """Adds ability to output line numbers in a new way."""

    # Capture `<span class="lineno">   1 </span>`
    RE_SPAN_NUMS = re.compile(
        r'(<span[^>]*?)(class="[^"]*\blinenos?\b[^"]*)"([^>]*)>([^<]+)(</span>)'
    )
    # Capture `<pre>` that is not followed by `<span></span>`
    RE_TABLE_NUMS = re.compile(r"(<pre[^>]*>)(?!<span></span>)")

    def __init__(self, **options):
        HtmlFormatter.__init__(self, **options)

    def _format_custom_line(self, m):
        """Format the custom line number."""
        return (
            m.group(1)
            + 'data-linenos="'
            + m.group(4)
            + '">'
            + m.group(5)
        )

    def _wrap_customlinenums(self, inner):
        """
        Wrapper to handle block inline line numbers.

        Don't display line numbers via `<span>  1</span>`,
        but include as `<span data-linenos="  1"></span>` and use CSS to display them:
        `[data-linenos]:before {content: attr(data-linenos);}`.
        This allows us to use inline and copy and paste without issue.
        """

        for tk, line in inner:
            if tk:
                line = self.RE_SPAN_NUMS.sub(self._format_custom_line, line)
            yield tk, line

    def wrap(self, source):
        """Wrap the source code."""
        if self.linenos == 2:  # "inline"
            source = self._wrap_customlinenums(source)
        return HtmlFormatter.wrap(self, source)


def block_code(
    code: str, info: str | None, *, escape: Callable[[str], str] = mistune.escape
) -> str:
    code = code.strip()
    info = (info or "").strip()

    if not info:
        return f"<pre><code>{escape(code)}</code></pre>\n"

    lang, *attrs = info.split(maxsplit=1)
    options = parse_attrs(attrs[0].strip() if attrs else "")
    options["cssclass"] = f"highlight lang-{lang}"
    options["wrapcode"] = True

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = CustomHtmlFormatter(**options)
        result = highlight(code, lexer, formatter)
        return result.replace("<pre><span></span><code>", "<pre><code>")

    except Exception:
        return f'<div class="lang-{lang}"><pre><code>{escape(code)}</code></pre></div>\n'


def parse_attrs(attrs_str: str) -> dict[str, t.Any]:
    attrs = {
        "linenos": False,
        "hl_lines": [],
        "linenostart": 1,
        "linenostep": 1,
        "filename": None,
    }

    # Surronding braces are optional
    attrs_str = attrs_str.lstrip("{").rstrip("}").strip()
    if not attrs_str:
        return attrs

    attrs_dict = dict(re.findall(r'(?P<key>\w+)="(?P<value>[^"]*)"', attrs_str))
    attrs = attrs_dict.copy()

    if "title" in attrs_dict:
        attrs["filename"] = attrs_dict["title"]

    if "linenums" in attrs_dict:
        attrs["linenos"] = "inline"
        start, *step = attrs_dict["linenums"].split()
        if start.isdigit():
            attrs["linenostart"] = int(start)
        if step and step[0].isdigit():
            attrs["linenostep"] = int(step[0])

    if "hl_lines" in attrs_dict:
        attrs["hl_lines"] = []
        for val in attrs_dict["hl_lines"].split():
            if "-" in val:
                start, end = val.split("-", 1)
                if start.isdigit() and end.isdigit():
                    attrs["hl_lines"].extend(
                        range(int(start), int(end) + 1)
                    )
            elif val.isdigit():
                attrs["hl_lines"].append(int(val))

    return attrs


class HighlightMixin(object):
    def block_code(self, code, info=None):
        return block_code(code, info or "")
