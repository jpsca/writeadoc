import re
import typing as t

from mistune.directives._base import BaseDirective, DirectivePlugin

from .utils import render_attrs


if t.TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown


class Container(DirectivePlugin):
    def parse(
        self, block: "BlockParser", m: re.Match[str], state: "BlockState"
    ) -> dict[str, t.Any]:
        attrs = dict(self.parse_options(m))
        attrs.setdefault("class", "")
        title = self.parse_title(m)
        attrs["class"] += f"{title} {attrs['class']}".strip()
        content = self.parse_content(m)
        return {
            "type": "div",
            "children": self.parse_tokens(block, content, state),
            "attrs": attrs,
        }

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register("div", self.parse)

        assert md.renderer is not None
        if md.renderer.NAME == "html":
            md.renderer.register("div", render_container)


def render_container(self: t.Any, text: str, **attrs: t.Any) -> str:
    html_attrs = render_attrs(attrs)
    return f"<div{html_attrs}>\n{text}</div>\n"
