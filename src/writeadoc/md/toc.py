import re
import typing as t
import unicodedata

from mistune.core import BlockState
from mistune.util import striptags


if t.TYPE_CHECKING:
    from mistune.markdown import Markdown


RX_ATTRS_IN_HEADER = re.compile(r"(?<!/)\{([^\n\r}]*)\}")


def slugify(value: str, separator: str = "-", unicode: bool = True) -> str:
    """Slugify a string, to make it URL friendly."""
    if not unicode:
        # Replace Extended Latin characters with ASCII, i.e. `žlutý` => `zluty`
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[{}\s]+".format(separator), separator, value)


def heading_id(token: dict[str, t.Any], index: int) -> str:
    if "id" in token.get("attrs", {}):
        return token["attrs"]["id"]
    value = RX_ATTRS_IN_HEADER.sub("", token["text"]).strip()
    return slugify(value)


def add_toc_hook(
    md: "Markdown",
    min_level: int = 1,
    max_level: int = 3,
) -> None:
    """Add a hook to save toc items into `state.env`.

    Arguments:
        md:
            Markdown instance
        min_level:
            Minimum heading level
        max_level:
            Maximum heading level

    """

    def toc_hook(md: "Markdown", state: "BlockState") -> None:
        headings = []
        number_headers = state.env.get("meta", {}).get("number_headers", False)

        for tok in state.tokens:
            if tok["type"] == "heading":
                level = tok["attrs"]["level"]
                if min_level <= level <= max_level:
                    headings.append(tok)

        # Compute ids from the original (un-numbered) heading text so anchors
        # stay stable regardless of numbering.
        for i, tok in enumerate(headings):
            tok["attrs"]["id"] = heading_id(tok, i)

        if number_headers:
            number_headings(state.tokens)

        toc_items = [normalize_toc_item(md, tok, parent=state) for tok in headings]

        # save items into state
        state.env["toc_items"] = toc_items

    md.before_render_hooks.append(toc_hook)


def number_headings(tokens: list[dict[str, t.Any]]) -> None:
    """Prepend hierarchical numbering to heading tokens of level >= 2.

    Mutates each heading token's ``text`` in place. The numbering scheme is:
    h2 -> ``"1. "``, ``"2. "``; h3 -> ``"1.1 "``, ``"1.2 "``; h4 -> ``"1.1.1 "``, etc.
    """
    counters: list[int] = []
    for tok in tokens:
        if tok.get("type") != "heading":
            continue
        level = tok["attrs"]["level"]
        if level < 2:
            continue

        depth = level - 1  # h2 -> depth 1, h3 -> depth 2, ...
        if len(counters) < depth:
            counters.extend([0] * (depth - len(counters)))
        else:
            del counters[depth:]
        counters[depth - 1] += 1

        if depth == 1:
            prefix = f'<span class="num">{counters[0]}.</span> '
        else:
            prefix = f'<span class="num">{".".join(str(n) for n in counters)}</span> '
        tok["text"] = prefix + tok["text"]


def normalize_toc_item(
    md: "Markdown",
    token: dict[str, t.Any],
    parent: t.Any | None = None,
) -> tuple[int, str, str]:
    text = token["text"]
    tokens = md.inline(text, parent.env if parent else {})
    assert md.renderer is not None
    html = md.renderer(tokens, BlockState())
    text = striptags(html)
    attrs = token["attrs"]
    return attrs["level"], attrs["id"], text
