import re
import typing as t

from mistune.directives._base import BaseDirective, DirectivePlugin


if t.TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown


class Admonition(DirectivePlugin):
    SUPPORTED_NAMES = {
        "note",
        "tip",
        "warning",
        "error",
        "new",
    }

    def parse(
        self, block: "BlockParser", m: re.Match[str], state: "BlockState"
    ) -> dict[str, t.Any]:
        name = self.parse_type(m)
        attrs: dict[str, t.Any] = {"name": name}
        options = dict(self.parse_options(m))
        if "class" in options:
            attrs["class"] = options["class"]
        if "collapsible" in options:
            attrs["collapsible"] = True
        if "open" in options:
            attrs["open"] = True

        title = self.parse_title(m)
        if not title:
            title = name.capitalize()

        content = self.parse_content(m)
        children = [
            {
                "type": "admonition_title",
                "text": title,
                "attrs": attrs,
            },
            {
                "type": "admonition_content",
                "children": self.parse_tokens(block, content, state),
            },
        ]
        return {
            "type": "admonition",
            "children": children,
            "attrs": attrs,
        }

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        for name in self.SUPPORTED_NAMES:
            directive.register(name, self.parse)

        assert md.renderer is not None
        if md.renderer.NAME == "html":
            md.renderer.register("admonition", render_admonition)
            md.renderer.register("admonition_title", render_admonition_title)
            md.renderer.register("admonition_content", render_admonition_content)


def render_admonition(self: t.Any, text: str, name: str, **attrs: t.Any) -> str:
    _cls = attrs.get("class")
    if _cls:
        _cls = " " + _cls

    if "collapsible" in attrs:
        _open = " open" if "open" in attrs and attrs["open"] else ""
        return f'<details class="admonition {name}{_cls}"{_open}>\n{text}</details>\n'

    return f'<section class="admonition {name}{_cls}">\n{text}</section>\n'


def render_admonition_title(self: t.Any, text: str, **attrs: t.Any) -> str:
    if "collapsible" in attrs:
        return '<summary class="admonition-title">' + text + "</summary>\n"

    return '<p class="admonition-title">' + text + "</p>\n"


def render_admonition_content(self: t.Any, text: str) -> str:
    return text
