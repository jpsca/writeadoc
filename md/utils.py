def quote(text: str) -> str:
    if '"' in text:
        if "'" in text:
            text = text.replace('"', "&quot;")
            return f'"{text}"'
        else:
            return f"'{text}'"

    return f'"{text}"'


TRUTHY_VALUES = {"True", "true",}
FALSY_VALUES = {"False", "false",}


def render_attrs(attrs: dict[str, str]) -> str:
    """Render a dictionary of attributes to a string suitable for HTML attributes."""
    properties = set()
    attributes = {}
    for name, value in attrs.items():
        name = name.replace("_", "-")
        if value in FALSY_VALUES:
            continue
        if value in TRUTHY_VALUES:
            properties.add(name)
        else:
            attributes[name] = value

    attributes = dict(sorted(attributes.items()))

    html_attrs = [
        f"{name}={quote(str(value))}"
        for name, value in attributes.items()
    ]
    html_attrs.extend(sorted(properties))

    return " ".join(html_attrs)
