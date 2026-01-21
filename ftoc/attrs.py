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
    attrs, _remainder = _scanner.scan(attrs_str)
    print(attrs, _remainder)
    return dict(attrs)


def parse_inline_attrs(inline: InlineParser, m: re.Match, state: InlineState):
    attrs_str = m.groupdict().get("inline_attrs")
    if attrs_str:
      attrs = parse_attrs(attrs_str)

      # Attach to the previous inline token
      if state.tokens:
          prev = state.tokens[-1]
          prev["attrs"] = attrs

    return m.end()


def inline_attrs(md: Markdown) -> None:
    md.inline.register(
        "inline_attrs",
        r"\{\s*([^\}]+)\s*\}",
        parse_inline_attrs,
        before="link"
    )
