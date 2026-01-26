import re
import typing as t

from mistune import InlineParser, InlineState
from mistune.markdown import Markdown


def _handle_double_quote(s, tk):
    k, v = tk.split("=", 1)
    return k, v.strip('"')


def _handle_single_quote(s, tk):
    k, v = tk.split("=", 1)
    return k, v.strip("'")


def _handle_key_value(s, tk):
    return tk.split("=", 1)


def _handle_word(s, tk):
    if tk.startswith("."):
        return ".", tk[1:]
    if tk.startswith("#"):
        return "id", tk[1:]
    return tk, True


_scanner = re.Scanner(  # type: ignore
    [
        (r'[^ =}]+=".*?"', _handle_double_quote),
        (r"[^ =}]+='.*?'", _handle_single_quote),
        (r"[^ =}]+=[^ =}]+", _handle_key_value),
        (r"[^ =}]+", _handle_word),
        (r" ", None),
    ]
)


def parse_attrs(attrs_str: str) -> dict[str, t.Any]:
    """Parse attribute list and return a list of attribute tuples.
    """
    attrs_str = attrs_str.strip("{}").strip()
    _attrs, _remainder = _scanner.scan(attrs_str)
    print(_attrs)

    attrs = {}
    classes = set()
    for k, v in _attrs:
        if k == ".":
            classes.add(v)
        elif k == "#":
            attrs["id"] = v
        else:
            attrs[k] = v

    if classes:
        str_classes = " ".join(classes)
        if "class" in attrs:
            attrs["class"] += " " + str_classes
        else:
            attrs["class"] = str_classes

    return dict(attrs)


def attach_attrs(inline: InlineParser, m: re.Match, state: InlineState):
    attrs_str = m.groupdict().get("attrs_list")
    if attrs_str:
      attrs = parse_attrs(attrs_str)

      # Attach to the previous token
      if state.tokens:
          prev = state.tokens[-1]
          prev["attrs"] = attrs

    return m.end()


def attrs_list(md: Markdown) -> None:
    md.inline.register(
        "attrs_list",
        r"\{\s*([^\}]+)\s*\}",
        attach_attrs,
        before="link"
    )
