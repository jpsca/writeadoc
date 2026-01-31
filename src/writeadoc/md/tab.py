import re
import typing as t

import mistune
from mistune.directives._base import BaseDirective, DirectivePlugin


if t.TYPE_CHECKING:
    from mistune.block_parser import BlockParser
    from mistune.core import BlockState
    from mistune.markdown import Markdown


class Tab(DirectivePlugin):
    """Tab directive for creating tabbed content panels.

    Syntax:
        ::: tab | Label with **markdown** support
        Content here with **markdown** support
        :::

    Consecutive tab directives are automatically grouped into a tabbed set.
    """

    def parse(
        self, block: "BlockParser", m: re.Match[str], state: "BlockState"
    ) -> dict[str, t.Any]:
        label = self.parse_title(m)
        content = self.parse_content(m)
        attrs = dict(self.parse_options(m))

        return {
            "type": "tab",
            "label": label,  # Raw text - will be inline-parsed during grouping
            "children": self.parse_tokens(block, content, state),
            "attrs": attrs,
        }

    def __call__(self, directive: "BaseDirective", md: "Markdown") -> None:
        directive.register("tab", self.parse)

        if md.renderer and md.renderer.NAME == "html":
            md.renderer.register("tab", render_tab)
            md.renderer.register("tabbed_set", render_tabbed_set)

        # Register the grouping hook (runs before rendering)
        def hook(markdown: "Markdown", state: "BlockState") -> None:
            _group_tabs_hook(markdown, state)

        md.before_render_hooks.append(hook)


def render_tab(self: t.Any, text: str, **attrs: t.Any) -> str:
    """Tab tokens are rendered by their parent tabbed_set, not individually."""
    return ""


def render_tabbed_set(
    self: t.Any,
    text: str,
    tabs: list,
    set_id: int,
    **attrs: t.Any,
) -> str:
    """Render a complete tabbed set from pre-rendered tab data."""
    inputs = []
    labels = []
    panels = []

    # Find which tab should be selected (default to first)
    selected_index = 0
    for i, tab in enumerate(tabs):
        if tab.get("select"):
            selected_index = i
            break

    for i, tab in enumerate(tabs):
        tab_id = f"__tabbed_{set_id}_{i + 1}"
        checked = " checked" if i == selected_index else ""

        inputs.append(
            f'<input id="{tab_id}" name="__tabbed_{set_id}" type="radio"{checked}>'
        )
        labels.append(f'<label for="{tab_id}">{tab["label_html"] or i + 1}</label>')
        panels.append(f'<div class="tabbed-panel">\n{tab["content_html"]}</div>')

    return (
        '<div class="tabbed-set">\n'
        + "\n".join(inputs)
        + "\n"
        + '<div class="tabbed-labels">\n'
        + "\n".join(labels)
        + "\n</div>\n"
        + '<div class="tabbed-panels">\n'
        + "\n".join(panels)
        + "\n</div>\n"
        + "</div>\n"
    )


def _group_tabs_hook(md: "Markdown", state: "BlockState") -> None:
    """Before-render hook that groups consecutive tab tokens into tabbed_set containers."""
    state.tokens = _group_consecutive_tabs(state.tokens, state, md)


def _group_consecutive_tabs(
    tokens: list[dict], state: "BlockState", md: "Markdown"
) -> list[dict]:
    """Transform token list to group consecutive tab tokens into tabbed_set containers."""
    result = []
    tab_buffer: list[dict] = []
    # Buffer blank lines that appear between tabs - they get discarded if followed by another tab
    blank_buffer: list[dict] = []

    for token in tokens:
        if token["type"] == "tab":
            # Check if this tab should start a new group
            if token["attrs"].get("new") and tab_buffer:
                result.append(_create_tabbed_set(tab_buffer, state, md))
                tab_buffer = []
            # Discard blank lines between tabs
            blank_buffer = []
            tab_buffer.append(token)
        elif token["type"] == "blank_line" and tab_buffer:
            # Potentially between tabs - buffer it
            blank_buffer.append(token)
        else:
            # Non-tab, non-blank token
            if tab_buffer:
                result.append(_create_tabbed_set(tab_buffer, state, md))
                tab_buffer = []
                # Add back any buffered blank lines (they weren't between tabs)
                result.extend(blank_buffer)
                blank_buffer = []
            # Recursively process children (e.g., tabs inside admonitions)
            if "children" in token:
                token["children"] = _group_consecutive_tabs(token["children"], state, md)
            result.append(token)

    # Flush remaining tabs at end
    if tab_buffer:
        result.append(_create_tabbed_set(tab_buffer, state, md))
    # Any trailing blank lines after tabs are discarded

    return result


def _create_tabbed_set(tabs: list[dict], state: "BlockState", md: "Markdown") -> dict:
    """Create a tabbed_set token from a list of tab tokens."""
    assert md.renderer is not None

    counter = state.env.setdefault("_tab_set_counter", 0) + 1
    state.env["_tab_set_counter"] = counter

    rendered_tabs = []
    for tab in tabs:
        # Render label as inline markdown
        if tab["label"]:
            inline_state = mistune.InlineState({})
            inline_state.src = tab["label"]
            label_tokens = md.inline.parse(inline_state)
            label_html = md.renderer.render_tokens(label_tokens, state)
        else:
            label_html = ""

        # Process children with _iter_render to convert 'text' to 'children'
        # This is necessary because before_render_hooks runs before _iter_render
        processed_children = list(md._iter_render(tab["children"], state))

        # Render content children as HTML
        content_html = md.renderer.render_tokens(processed_children, state)

        rendered_tabs.append(
            {
                "label_html": label_html,
                "content_html": content_html,
                "select": tab["attrs"].get("select"),
            }
        )

    return {
        "type": "tabbed_set",
        "children": [],  # Empty - Mistune won't auto-render
        "attrs": {
            "set_id": counter,
            "tabs": rendered_tabs,
        },
    }
