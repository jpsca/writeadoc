import re
import typing as t

from mistune.directives._base import BaseDirective, DirectivePlugin

from .utils import render_attrs


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
        attrs = dict(self.parse_options(m))
        attrs.setdefault("class", "")
        attrs["class"] += f"admonition {name} {attrs['class']}".strip()

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


def render_admonition(self: t.Any, text: str, **attrs: t.Any) -> str:
    html_attrs = render_attrs(attrs)

    if "open" in attrs:
        return f"<details{html_attrs}>\n{text}</details>\n"
    else:
        return f"<section{html_attrs}>\n{text}</section>\n"


def render_admonition_title(self: t.Any, text: str, **attrs: t.Any) -> str:
    if "open" in attrs:
        return f'<summary class="admonition-title">{text}</summary>\n'
    else:
        return f'<p class="admonition-title">{text}</p>\n'


def render_admonition_content(self: t.Any, text: str) -> str:
    return text
