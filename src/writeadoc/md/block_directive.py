import re
import typing as t

from mistune.directives import DirectivePlugin, FencedDirective


if t.TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState


_directive_re = re.compile(
    r"\s*(?P<type>[a-zA-Z0-9_-]+)(\s*\|)? *(?P<title>[^\n]*)(?:\n|$)"
    r"(?P<options>(?:\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)"
    r"\n*(?P<text>(?:[^\n]*\n+)*)"
)


class BlockDirective(FencedDirective):
    """A **fenced** style of directive that uses the more popular `:::` syntax
    and removes the braces around the directive type.

    The syntax looks like:

    ```markdown
    ::: directive-type title
    :option-key: option-value
    :option-key: option-value

    content text here
    :::
    """
    def __init__(self, plugins: list[DirectivePlugin]) -> None:
        super().__init__(plugins, markers=":")
        _marker_pattern = re.escape(self.markers)
        self.directive_pattern = (
            r"^(?P<fenced_directive_mark>(?:" + _marker_pattern + r"){3,})"
            r"\s*[a-zA-Z0-9_-]+"
        )

    def _process_directive(self, block: "BlockParser", marker: str, start: int, state: "BlockState") -> int | None:
        mlen = len(marker)
        cursor_start = start + len(marker)

        _end_pattern = (
            r"^ {0,3}" + marker[0] + "{" + str(mlen) + r",}"
            r"[ \t]*(?:\n|$)"
        )
        _end_re = re.compile(_end_pattern, re.M)

        _end_m = _end_re.search(state.src, cursor_start)
        if _end_m:
            text = state.src[cursor_start : _end_m.start()]
            end_pos = _end_m.end()
        else:
            text = state.src[cursor_start:]
            end_pos = state.cursor_max

        m = _directive_re.match(text)
        if not m:
            return None

        self.parse_method(block, m, state)
        return end_pos
