from mistune.util import escape_url, safe_entity


URL_ATTRS = ("href", "src", "action", "formaction")
TRUTHY_VALUES = ("True", "true",)
FALSY_VALUES = ("False", "false")


def quote(text: str) -> str:
    if '"' in text:
        if "'" in text:
            text = text.replace('"', "&quot;")
            return f'"{text}"'
        else:
            return f"'{text}'"
    return f'"{text}"'


def escape_value(name: str, value: str) -> str:
    """Escape attribute value."""
    if name in URL_ATTRS:
        value = escape_url(value)
    else:
        value = safe_entity(value)
    return value


def render_attrs(attrs: dict[str, str | int]) -> str:
    """Render a dictionary of attributes to a string suitable for HTML attributes."""
    properties = set()
    attributes = {}
    for name, value in attrs.items():
        name = name.replace("_", "-")
        str_value = str(value).lower()
        if str_value.lower() == "false":
            continue
        if str_value == "true":
            properties.add(name)
        else:
            attributes[name] = escape_value(name, str(value))

    attributes = dict(sorted(attributes.items()))

    html_attrs = [
        f"{name}={quote(str(value))}"
        for name, value in attributes.items()
    ]
    html_attrs.extend(sorted(properties))

    if html_attrs:
        return f" {' '.join(html_attrs)}"
    else:
        return ""

