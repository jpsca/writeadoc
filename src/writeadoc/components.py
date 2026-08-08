"""Rendering of the Jx components embedded in the HTML produced from markdown.

This is the second half of a feature whose first half lives in `md/mdjx.py`.
That one is a mistune plugin: it keeps tags that start with an uppercase letter
(`<Card>…</Card>`) as raw block HTML, so markdown never rewrites what is inside
them. This module takes that HTML and hands it to Jx to render.

Braces are what makes it awkward. Markdown output routinely contains literal
`{` and `}` that Jinja must not interpret, in code blocks or CSS snippets, so
every brace is swapped for a sentinel character before rendering and swapped
back afterwards. The exception is the `{% fill %}` tags written inside a
component's body: those are real Jinja and have to survive the swap, so they are
pulled out first and put back once the braces are neutralized.
"""

import re
from collections.abc import Callable


__all__ = ("render_components",)


RX_FILL_TAG = re.compile(
    r"{%-?\s*(?:fill\s+[0-9A-Za-z_.:$-]+|endfill)\s*-?%}"
)

# Sentinels standing in for braces, and for a lifted `{% fill %}` tag. They are
# control characters, so they cannot collide with anything in the page.
OPEN_REPL = "\u0002"
CLOSE_REPL = "\u0003"
FILL_OPEN = "\u0004"
FILL_CLOSE = "\u0005"


def render_components(
    html: str,
    imports: dict[str, str],
    *,
    render_string: Callable[[str], str],
) -> str:
    """Render the components used in a page, leaving literal braces alone.

    Arguments:
        html: The HTML produced from the markdown source.
        imports: The components to import, by name, from the page metadata.
        render_string: Renders a template source, normally `Catalog.render_string`.

    Returns:
        The HTML with every component rendered.

    """
    html, fill_tags = protect_fill_tags(html, imports)

    html = html.replace("{", OPEN_REPL).replace("}", CLOSE_REPL)
    for token, tag in fill_tags:
        html = html.replace(token, tag)

    jx_imports = "\n".join(
        f'{{# import "{path}" as {name} #}}' for name, path in imports.items()
    )
    rendered = str(render_string(f"{jx_imports}\n{html}"))
    return rendered.replace(OPEN_REPL, "{").replace(CLOSE_REPL, "}")


def protect_fill_tags(
    source: str,
    imports: dict[str, str],
) -> tuple[str, list[tuple[str, str]]]:
    """Lift the `{% fill %}` tags written inside a component's body.

    Returns the source with each of them replaced by a sentinel token, and the
    tokens paired with the tag they stand for.
    """
    if "{%" not in source:
        return source, []

    names = [re.escape(name) for name in imports]
    if not names:
        return source, []

    tag_rx = re.compile(rf"<(?P<tag>{'|'.join(names)})(?=\s|/|>)")
    fill_tags: list[tuple[str, str]] = []

    def protect_fill(match: re.Match[str]) -> str:
        token = f"{FILL_OPEN}WAD_FILL_{len(fill_tags)}{FILL_CLOSE}"
        fill_tags.append((token, match.group(0)))
        return token

    result = []
    pos = 0

    while match := tag_rx.search(source, pos):
        tag = match.group("tag")
        tag_end = find_tag_end(source, match.end())
        if tag_end == -1:
            pos = match.end()
            continue

        if source[match.start():tag_end].rstrip().endswith("/>"):
            pos = tag_end
            continue

        close_start, close_end = find_closing_tag(source, tag, tag_end)
        if close_start == -1:
            pos = tag_end
            continue

        result.append(source[pos:tag_end])
        result.append(RX_FILL_TAG.sub(protect_fill, source[tag_end:close_start]))
        result.append(source[close_start:close_end])
        pos = close_end

    if not result:
        return source, fill_tags

    result.append(source[pos:])
    return "".join(result), fill_tags


def find_closing_tag(source: str, tag: str, pos: int) -> tuple[int, int]:
    """Locate the closing tag matching an already open one, honoring nesting.

    Returns the start and end offsets of the closing tag, or `(-1, -1)` if the
    tag is never closed.
    """
    open_rx = re.compile(rf"<{re.escape(tag)}(?=\s|/|>)")
    close_tag = f"</{tag}>"
    close_len = len(close_tag)
    depth = 1

    while depth:
        next_open = open_rx.search(source, pos)
        next_close = source.find(close_tag, pos)

        if next_close == -1:
            return -1, -1

        if next_open and next_open.start() < next_close:
            tag_end = find_tag_end(source, next_open.end())
            if tag_end == -1:
                return -1, -1
            if not source[next_open.start():tag_end].rstrip().endswith("/>"):
                depth += 1
            pos = tag_end
            continue

        depth -= 1
        if depth == 0:
            return next_close, next_close + close_len
        pos = next_close + close_len

    return -1, -1


def find_tag_end(source: str, pos: int) -> int:
    """Offset just past the `>` closing an opening tag, ignoring quoted `>`.

    Returns -1 if the tag is never closed.
    """
    in_single_quotes = False
    in_double_quotes = False

    for i in range(pos, len(source)):
        ch = source[i]
        if ch == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
        elif ch == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
        elif ch == ">" and not in_single_quotes and not in_double_quotes:
            return i + 1

    return -1
