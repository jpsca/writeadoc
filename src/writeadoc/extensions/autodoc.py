from collections.abc import Callable
import re
import xml.etree.ElementTree as ElementTree

from markdown.blockparser import BlockParser
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension


class AutodocBlockProcessor(BlockProcessor):
    RE_AUTODOC = re.compile(r"^:::\s*([\w\.]+)(?:\s+(\d+))?\s*$")

    def __init__(self, parser: BlockParser, renderer: Callable[[str, int | None], str]):
        super().__init__(parser)
        self.renderer = renderer

    def test(self, parent, block):
        return self.RE_AUTODOC.match(block) is not None

    def run(self, parent, blocks):
        block = blocks.pop(0)
        match = self.RE_AUTODOC.match(block)
        if match:
            name = match.group(1) or ""
            level = match.group(2)
            level = int(level) if level is not None else None
            markdown_content = self.renderer(name, level)

            # Process the content directly using markdown
            tmp = ElementTree.Element("div")
            self.parser.parseChunk(tmp, markdown_content)

            # Extract processed elements
            for child in tmp:
                parent.append(child)

            return True
        return False


def fallback_renderer(x: str, y: int | None = None):
    return f"Autodoc for {x} at level {y}"


class AutodocExtension(Extension):
    def __init__(
        self,
        renderer: Callable[[str, int | None], str] = fallback_renderer,
        **kwargs,
    ):
        self.config = {
            "renderer": [
                renderer,
                "Function to render autodoc content",
            ]
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        # Get render function from config
        renderer = self.getConfig("renderer")
        # Register with high priority to process before other block processors
        md.parser.blockprocessors.register(
            AutodocBlockProcessor(md.parser, renderer=renderer), "autodoc", 200
        )


def makeExtension(**kwargs):
    return AutodocExtension(**kwargs)
