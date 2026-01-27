"""
Mistune plugins to support additional inline formatting.

Copyright (c) 2014, Hsiaoming Yang
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of the creator nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import re
import typing as t

from mistune.helpers import PREVENT_BACKSLASH

from .utils import render_attrs


if t.TYPE_CHECKING:
    from mistune.core import BaseRenderer, InlineState
    from mistune.inline_parser import InlineParser
    from mistune.markdown import Markdown


__all__ = ["strikethrough", "mark", "insert", "superscript", "subscript"]

_STRIKE_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\~|[^\s~])~~(?!~)")
_MARK_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\=|[^\s=])==(?!=)")
_INSERT_END = re.compile(r"(?:" + PREVENT_BACKSLASH + r"\\\^|[^\s^])\^\^(?!\^)")

SUPERSCRIPT_PATTERN = r"\^(?:" + PREVENT_BACKSLASH + r"\\\^|\S|\\ )+?\^"
SUBSCRIPT_PATTERN = r"~(?:" + PREVENT_BACKSLASH + r"\\~|\S|\\ )+?~"


def parse_strikethrough(inline: "InlineParser", m: re.Match[str], state: "InlineState") -> int | None:
    return _parse_to_end(inline, m, state, "strikethrough", _STRIKE_END)


def render_strikethrough(renderer: "BaseRenderer", text: str, **attrs: t.Any) -> str:
    return f"<del{render_attrs(attrs)}>{text}</del>"


def parse_mark(inline: "InlineParser", m: re.Match[str], state: "InlineState") -> int | None:
    return _parse_to_end(inline, m, state, "mark", _MARK_END)


def render_mark(renderer: "BaseRenderer", text: str, **attrs: t.Any) -> str:
    return f"<mark{render_attrs(attrs)}>{text}</mark>"


def parse_insert(inline: "InlineParser", m: re.Match[str], state: "InlineState") -> int | None:
    return _parse_to_end(inline, m, state, "insert", _INSERT_END)


def render_insert(renderer: "BaseRenderer", text: str, **attrs: t.Any) -> str:
    return f"<ins{render_attrs(attrs)}>{text}</ins>"


def parse_superscript(inline: "InlineParser", m: re.Match[str], state: "InlineState") -> int:
    return _parse_script(inline, m, state, "superscript")


def render_superscript(renderer: "BaseRenderer", text: str, **attrs: t.Any) -> str:
    return f"<sup{render_attrs(attrs)}>{text}</sup>"


def parse_subscript(inline: "InlineParser", m: re.Match[str], state: "InlineState") -> int:
    return _parse_script(inline, m, state, "subscript")


def render_subscript(renderer: "BaseRenderer", text: str, **attrs: t.Any) -> str:
    return f"<sub{render_attrs(attrs)}>{text}</sub>"


def _parse_to_end(
    inline: "InlineParser",
    m: re.Match[str],
    state: "InlineState",
    tok_type: str,
    end_pattern: re.Pattern[str],
) -> int | None:
    pos = m.end()
    m1 = end_pattern.search(state.src, pos)
    if not m1:
        return None
    end_pos = m1.end()
    text = state.src[pos : end_pos - 2]
    new_state = state.copy()
    new_state.src = text
    children = inline.render(new_state)
    state.append_token({"type": tok_type, "children": children})
    return end_pos


def _parse_script(inline: "InlineParser", m: re.Match[str], state: "InlineState", tok_type: str) -> int:
    text = m.group(0)
    new_state = state.copy()
    new_state.src = text[1:-1].replace("\\ ", " ")
    children = inline.render(new_state)
    state.append_token({"type": tok_type, "children": children})
    return m.end()


def strikethrough(md: "Markdown") -> None:
    """A mistune plugin to support strikethrough. Spec defined by
    GitHub flavored Markdown and commonly used by many parsers:

    .. code-block:: text

        ~~This was mistaken text~~

    It will be converted into HTML:

    .. code-block:: html

        <del>This was mistaken text</del>

    :param md: Markdown instance
    """
    md.inline.register(
        "strikethrough",
        r"~~(?=[^\s~])",
        parse_strikethrough,
        before="link",
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("strikethrough", render_strikethrough)


def mark(md: "Markdown") -> None:
    """A mistune plugin to add ``<mark>`` tag. Spec defined at
    https://facelessuser.github.io/pymdown-extensions/extensions/mark/:

    .. code-block:: text

        ==mark me== ==mark \\=\\= equal==

    :param md: Markdown instance
    """
    md.inline.register(
        "mark",
        r"==(?=[^\s=])",
        parse_mark,
        before="link",
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("mark", render_mark)


def insert(md: "Markdown") -> None:
    """A mistune plugin to add ``<ins>`` tag. Spec defined at
    https://facelessuser.github.io/pymdown-extensions/extensions/caret/#insert:

    .. code-block:: text

        ^^insert me^^

    :param md: Markdown instance
    """
    md.inline.register(
        "insert",
        r"\^\^(?=[^\s\^])",
        parse_insert,
        before="link",
    )
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("insert", render_insert)


def superscript(md: "Markdown") -> None:
    """A mistune plugin to add ``<sup>`` tag. Spec defined at
    https://pandoc.org/MANUAL.html#superscripts-and-subscripts:

    .. code-block:: text

        2^10^ is 1024.

    :param md: Markdown instance
    """
    md.inline.register("superscript", SUPERSCRIPT_PATTERN, parse_superscript, before="linebreak")
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("superscript", render_superscript)


def subscript(md: "Markdown") -> None:
    """A mistune plugin to add ``<sub>`` tag. Spec defined at
    https://pandoc.org/MANUAL.html#superscripts-and-subscripts:

    .. code-block:: text

        H~2~O is a liquid.

    :param md: Markdown instance
    """
    md.inline.register("subscript", SUBSCRIPT_PATTERN, parse_subscript, before="linebreak")
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("subscript", render_subscript)
