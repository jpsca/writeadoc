import re
import typing as t

from mistune import BlockParser, BlockState, InlineParser, InlineState
from mistune.markdown import Markdown


RE_ATTRS = r"\{\s*([^\}]+)\s*\}"


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

    attrs = {}
    classes = {}
    for k, v in _attrs:
        if k == ".":
            classes[v] = 1
        elif k == "#":
            attrs["id"] = v
        else:
            attrs[k] = v

    if classes:
        str_classes = " ".join(classes.keys())
        if "class" in attrs:
            attrs["class"] += " " + str_classes
        else:
            attrs["class"] = str_classes

    return dict(attrs)


def attach_inline_attrs(inline: InlineParser, m: re.Match, state: InlineState) -> int:
    attrs_str = m.groupdict().get("inline_attrs")
    if attrs_str and state.tokens:
        prev = state.tokens[-1]
        attrs = parse_attrs(attrs_str)
        prev.setdefault("attrs", {})
        prev["attrs"].update(attrs)
    return m.end()


def attach_block_attrs(block: BlockParser, m: re.Match, state: BlockState) -> int:
    attrs_str = m.groupdict().get("block_attrs")
    if attrs_str and state.tokens:
        prev = state.tokens[-1]
        attrs = parse_attrs(attrs_str)
        prev.setdefault("attrs", {})
        prev["attrs"].update(attrs)
    return m.end()


def inline_attrs(md: Markdown) -> None:
    md.inline.register(
        "inline_attrs",
        RE_ATTRS,
        attach_inline_attrs,
        before="link"
    )

def block_attrs(md: Markdown) -> None:
    md.block.register(
        "block_attrs",
        rf"^\s*{RE_ATTRS}\s$",
        attach_block_attrs,
    )
