"""Plugin to treat uppercase HTML tags as block-level raw HTML, later
to be rendered by Jx (if imports are set up).

This allows custom component tags like <Card>, <Test>, <Header> to be
treated as block HTML when they appear on their own (with blank lines
around them), preventing markdown processing inside them.
"""
import re
import typing as t

from mistune import BlockParser, BlockState
from mistune.markdown import Markdown


if t.TYPE_CHECKING:
    from mistune.core import BaseRenderer


def parse_mdjx(block: BlockParser, m: re.Match[str], state: BlockState) -> int:
    """Parse uppercase HTML tags as block HTML."""
    text = m.group(0)
    end_pos = m.end() + 1  # Position after trailing newline
    state.append_token({"type": "mdjx", "raw": text})
    return end_pos


def render_mdjx(renderer: "BaseRenderer", raw: str) -> str:
    return raw + "\n"


def mdjx(md: Markdown) -> None:
    """Register the custom block HTML rule.

    This rule matches HTML tags that start with an uppercase letter
    (e.g., <Card>, <Test>) when they appear as block-level elements
    (on their own line with optional leading spaces).

    The content inside these tags is NOT processed as markdown.
    """
    # Pattern to match uppercase tags as block HTML
    # Supports both self-closing tags (<Tag />) and paired tags (<Tag>...</Tag>)
    #
    # Attribute pattern: (?:[^>"']|"[^"]*"|'[^']*')*
    # This properly handles > characters inside quoted attribute values by matching:
    # - [^>"'] - any char except >, ", or '
    # - "[^"]*" - double-quoted strings
    # - '[^']*' - single-quoted strings
    #
    # Note: Nested tags with the same name are not supported (e.g., <Test><Test></Test></Test>)
    # The lazy match will stop at the first closing tag found.
    ATTR = r"(?:[^>\"']|\"[^\"]*\"|'[^']*')*"
    pattern = (
        r"^[ ]{0,3}(?:"
        rf"<[A-Z][a-zA-Z0-9]*{ATTR}/>"  # Self-closing tag
        r"|"
        rf"<(?P<_customtag>[A-Z][a-zA-Z0-9]*){ATTR}>[\s\S]*?</(?P=_customtag)>"  # Paired tags
        r")[ \t]*$"
    )
    md.block.register("mdjx", pattern, parse_mdjx, before="raw_html")
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("mdjx", render_mdjx)
