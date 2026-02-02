"""Plugin to treat uppercase HTML tags as block-level raw HTML.

This allows custom component tags like <Card>, <Test>, <Header> to be
treated as block HTML when they appear on their own (with blank lines
around them), preventing markdown processing inside them.
"""
import re

from mistune import BlockParser, BlockState
from mistune.markdown import Markdown


def parse_custom_html(
    block: BlockParser, m: re.Match[str], state: BlockState
) -> int:
    """Parse uppercase HTML tags as block HTML."""
    text = m.group(0)
    end_pos = m.end() + 1  # Position after trailing newline

    # Check if another uppercase tag follows immediately (no blank line).
    # If so, don't add newline to raw (renderer will add one anyway).
    remaining = state.src[end_pos:]
    if re.match(r"[ ]{0,3}<[A-Z]", remaining):
        # Another uppercase tag follows - don't add extra newline
        state.append_token({"type": "block_html", "raw": text})
    else:
        # Followed by blank line or other content - add newline for proper spacing
        state.append_token({"type": "block_html", "raw": text + "\n"})

    return end_pos


def custom_block_html(md: Markdown) -> None:
    """Register the custom block HTML rule.

    This rule matches HTML tags that start with an uppercase letter
    (e.g., <Card>, <Test>) when they appear as block-level elements
    (on their own line with optional leading spaces).

    The content inside these tags is NOT processed as markdown.
    """
    # Pattern to match uppercase tags as block HTML
    # - ^[ ]{0,3} - start of line with up to 3 spaces (standard block indent)
    # - <(?P<_customtag>[A-Z][a-zA-Z0-9]*) - opening tag starting with uppercase
    # - (?:\s[^>]*)? - optional attributes
    # - > - close of opening tag
    # - [\s\S]*? - content (lazy match, including newlines)
    # - </(?P=_customtag)> - matching closing tag (backreference)
    # - [ \t]*$ - optional trailing whitespace, end of line
    pattern = (
        r"^[ ]{0,3}<(?P<_customtag>[A-Z][a-zA-Z0-9]*)(?:\s[^>]*)?>"
        r"[\s\S]*?</(?P=_customtag)>[ \t]*$"
    )
    md.block.register("custom_html", pattern, parse_custom_html, before="raw_html")
