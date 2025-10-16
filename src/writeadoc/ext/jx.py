import re

from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor


re_tag_name = r"[A-Z][0-9A-Za-z_.:$-]*"


class JXTagPreprocessor(Preprocessor):
    """
    Processes HTML tags that start with uppercase letter
    and replaces them with marked divs before parsing.
    """

    RX_OPEN = re.compile(fr"<\s?({re_tag_name})\b")
    RE_OPEN_REPL = r'<div tag="\1"'

    RX_CLOSE = re.compile(fr"</\s?({re_tag_name})\s*>")
    RE_CLOSE_REPL = r'<meta tag="\1"></div>'

    def run(self, lines):
        new_lines = []
        for line in lines:
            line = self.RX_OPEN.sub(self.RE_OPEN_REPL, line)
            line = self.RX_CLOSE.sub(self.RE_CLOSE_REPL, line)
            new_lines.append(line)
        return new_lines


class JXTagPostprocessor(Postprocessor):
    """
    Reverts the transformation done by JXTagProcessor
    """

    RX_OPEN = re.compile(fr'<div(.*?) tag="({re_tag_name})"', re.DOTALL)
    RE_OPEN_REPL = r"<\2\1"

    RX_CLOSE = re.compile(fr'<meta tag="({re_tag_name})">(</p>\n)?</div>')
    RE_CLOSE_REPL = r"\2</\1>"

    RX_OPEN2 = re.compile(fr"&lt;div tag=&quot;({re_tag_name})&quot;")
    RE_OPEN2_REPL = r"&lt;\1"

    RX_CLOSE2 = re.compile(fr"&lt;meta tag=&quot;({re_tag_name})&quot;&gt;&lt;/div&gt;")
    RE_CLOSE2_REPL = r"&lt;/\1&gt;"

    def run(self, text):
        # Restore tags
        text = self.RX_OPEN.sub(self.RE_OPEN_REPL, text)
        text = self.RX_CLOSE.sub(self.RE_CLOSE_REPL, text)

        # Restore tags that were escaped by Markdown (inside code blocks, etc.)
        text = self.RX_OPEN2.sub(self.RE_OPEN2_REPL, text)
        text = self.RX_CLOSE2.sub(self.RE_CLOSE2_REPL, text)

        return text


class JXExtension(Extension):
    """
    Python Markdown extension to handle JX tags
    """

    def extendMarkdown(self, md):
        md.preprocessors.register(JXTagPreprocessor(md), "jx_marker", 40)
        md.postprocessors.register(JXTagPostprocessor(md), "jx_restore", 10)


def makeExtension(**kwargs):
    return JXExtension(**kwargs)
