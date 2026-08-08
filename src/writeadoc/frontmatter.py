"""Reading and writing the `---` metadata block of a markdown page.

Front matter is parsed with `strictyaml`, but written back with the small
serializer below rather than with `strictyaml.as_document().as_yaml()`, which
renders booleans as `yes`/`no`, indents lists differently, and raises on a
`None` value.
"""

import typing as t

import strictyaml

from .exceptions import InvalidFrontMatter


if t.TYPE_CHECKING:
    # Type-only: importing it at runtime would make `types` and this module
    # import each other.
    from .types import TMetadata


__all__ = ("extract_metadata", "render_metadata")


META_START = "---"


def extract_metadata(source: str) -> tuple[str, "TMetadata"]:
    """Split a markdown source into its body and its front matter."""
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].strip() != META_START:
        return source, {}

    front_matter = ""
    body = ""
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == META_START:
            front_matter = "".join(lines[1:i])
            body = "".join(lines[i + 1:])
            break
    else:
        raise InvalidFrontMatter(
            truncate(source),
            "Missing closing front matter delimiter",
        )

    try:
        data = strictyaml.load(front_matter).data
        if isinstance(data, dict):
            meta = {**data}
        else:
            meta = {}
    except Exception as err:
        raise InvalidFrontMatter(truncate(body), *err.args) from err

    return body.strip(), meta


def render_metadata(meta: "TMetadata", **kwargs) -> str:
    """Render metadata as a front matter block."""
    meta = {**meta, **kwargs}
    if not meta:
        return ""
    yaml_content = dict_to_yaml(meta)
    return f"---\n{yaml_content}\n---"


def truncate(source: str, limit: int = 400) -> str:
    if len(source) > limit:
        return f"{source[: limit - 3]}..."
    return source


def dict_to_yaml(data: dict, indent: int = 0, is_list_item: bool = False) -> str:
    """Convert a Python dictionary to a YAML string.

    Args:
        data: The dictionary to convert
        indent: Current indentation level (for recursive calls)
        is_list_item: Whether the current item is part of a list

    Returns:
        A formatted YAML string representation
    """
    lines = []
    spaces = " " * indent

    if not data and isinstance(data, dict):
        return "{}" if indent == 0 else "{}"

    for key, value in data.items():
        if isinstance(value, dict):
            if not value:  # Empty dict
                lines.append(f"{spaces}{key}: {{}}")
            else:
                lines.append(f"{spaces}{key}:")
                lines.append(dict_to_yaml(value, indent + 2))
        elif isinstance(value, list):
            if not value:  # Empty list
                lines.append(f"{spaces}{key}: []")
            else:
                lines.append(f"{spaces}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{spaces}  -")
                        lines.append(dict_to_yaml(item, indent + 4, True))
                    else:
                        lines.append(f"{spaces}  - {_format_yaml_value(item)}")
        else:
            prefix = "" if is_list_item else f"{key}: "
            lines.append(f"{spaces}{prefix}{_format_yaml_value(value)}")

    return "\n".join(lines)


def _format_yaml_value(value) -> str:
    """Format a Python value as a YAML value."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        if any(char in value for char in ":#{}[],'\"\\"):
            # Quote strings with special characters
            # Escape any existing double quotes
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        return value
    return str(value)
