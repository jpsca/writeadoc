import re
import typing as t

from mistune.directives._base import BaseDirective, DirectivePlugin

from .utils import render_attrs


if t.TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown


class Figure(DirectivePlugin):
    def parse(
        self, block: "BlockParser", m: re.Match[str], state: "BlockState"
    ) -> dict[str, t.Any]:
        attrs = dict(self.parse_options(m))
        attrs["caption"] = (self.parse_title(m) or "").strip()
        content = self.parse_content(m)
        return {
            "type": "figure",
            "text": content,
            "attrs": attrs,
        }

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register("figure", self.parse)
        assert md.renderer is not None
        if md.renderer.NAME == "html":
            md.renderer.register("figure", render_figure)


def render_figure(self: t.Any, text: str, **attrs: t.Any) -> str:
    caption = attrs.pop("caption", "")
    html_attrs = render_attrs(attrs)
    html = f"<figure{html_attrs}>\n{text}\n"
    if caption:
        html = f"{html}<figcaption>{caption}</figcaption>\n"
    return f"{html}</figure>\n"
