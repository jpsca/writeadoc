import re

import jx
from jx.parser import re_tag_name


RX_BLOCK_TAG = re.compile(rf"<(?P<tag>{re_tag_name})\b.*>.*</(?P=tag)>", re.DOTALL)
RX_INLINE_TAG = re.compile(rf"<(?P<tag>{re_tag_name})\b.*/>", re.DOTALL)


def render_jx(catalog: jx.Catalog, source: str, imports: dict[str, str]) -> str:
    """Find and render individual Jx components in the source string.

    Args:
        catalog:
            The Jx Catalog instance to use for rendering.
        source:
            The source string containing Jx components.
        imports:
            A dictionary of `name: path` imports to be used in rendering.

    Returns:
        The source string with the Jx components named in `imports` rendered to HTML.

    """
    for RX in (RX_BLOCK_TAG, RX_INLINE_TAG):
        while True:
            match = RX.search(source)
            if not match:
                break
            source = replace_tag(catalog, source, imports, match)

    return source


def replace_tag(
    catalog: jx.Catalog,
    source: str,
    imports: dict[str, str],
    match: re.Match,
) -> str:
    """Replace a single Jx tag in the source string with its rendered HTML.

    Args:
        catalog:
            The Jx Catalog instance to use for rendering.
        source:
            The source string containing Jx components.
        match:
            A regex match object for the Jx tag to be replaced.

    Returns:
        The source string with the specified Jx tag replaced by its rendered HTML.

    """
    name = match.group("tag")
    if name not in imports:
        return source  # Unknown tag, leave as-is

    start = match.start()
    end = match.end()
    jx_import = f'{{# import "{imports[name]}" as {name} #}}'
    jx_source = source[start:end]

    rendered = catalog.render_string(f"{jx_import}\n{jx_source}")
    return f"{source[: start]}{rendered}{source[end :]}"
