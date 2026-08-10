"""Unit tests for the tag scanning behind `render_components`.

The end-to-end behavior is covered by `test_mdjx.py`, which builds real projects.
These cover the scanning edge cases that are awkward to reach from a markdown
file: quoted `>`, tags nested inside a tag of the same name, and self-closing
tags.
"""

import jx
import pytest

from writeadoc.components import (
    find_closing_tag,
    find_tag_end,
    protect_fill_tags,
    render_components,
)


IMPORTS = {"Card": "card.jx"}


class TestFindTagEnd:

    def test_plain_tag(self):
        source = "<Card>body</Card>"
        assert find_tag_end(source, len("<Card")) == len("<Card>")

    def test_greater_than_inside_a_double_quoted_value_is_not_the_end(self):
        source = '<Card title="a > b">body</Card>'
        assert find_tag_end(source, len("<Card")) == source.index(">body") + 1

    def test_greater_than_inside_a_single_quoted_value_is_not_the_end(self):
        source = "<Card title='a > b'>body</Card>"
        assert find_tag_end(source, len("<Card")) == source.index(">body") + 1

    def test_unterminated_tag(self):
        assert find_tag_end('<Card title="oops', len("<Card")) == -1


class TestFindClosingTag:

    def test_matches_the_only_closing_tag(self):
        source = "<Card>body</Card>"
        start, end = find_closing_tag(source, "Card", len("<Card>"))
        assert source[start:end] == "</Card>"

    def test_skips_the_closing_tag_of_a_nested_tag_of_the_same_name(self):
        source = "<Card>outer <Card>inner</Card> tail</Card>"
        start, end = find_closing_tag(source, "Card", len("<Card>"))

        assert start == source.rindex("</Card>")
        assert source[start:end] == "</Card>"

    def test_a_nested_self_closing_tag_does_not_open_a_level(self):
        source = "<Card>before <Card /> after</Card>"
        start, _ = find_closing_tag(source, "Card", len("<Card>"))

        assert start == source.index("</Card>")

    def test_unclosed_tag(self):
        assert find_closing_tag("<Card>body", "Card", len("<Card>")) == (-1, -1)


class TestProtectFillTags:

    def test_fill_tags_inside_a_component_are_lifted(self):
        source = "<Card>{% fill title %}Hi{% endfill %}</Card>"
        result, fill_tags = protect_fill_tags(source, IMPORTS)

        assert [tag for _, tag in fill_tags] == ["{% fill title %}", "{% endfill %}"]
        for token, tag in fill_tags:
            assert token in result
            assert tag not in result

    def test_fill_tags_outside_a_component_are_left_alone(self):
        source = "{% fill title %}<Card>body</Card>"
        result, fill_tags = protect_fill_tags(source, IMPORTS)

        assert fill_tags == []
        assert result == source

    def test_a_self_closing_tag_has_no_body(self):
        """So a stray closing tag after it must not be taken as its own."""
        source = "<Card /> {% fill title %} </Card>"
        result, fill_tags = protect_fill_tags(source, IMPORTS)

        assert fill_tags == []
        assert result == source

    def test_source_without_jinja_tags_is_untouched(self):
        source = "<Card>body</Card>"
        assert protect_fill_tags(source, IMPORTS) == (source, [])

    def test_source_without_imports_is_untouched(self):
        source = "<Card>{% fill title %}Hi{% endfill %}</Card>"
        assert protect_fill_tags(source, {}) == (source, [])


class TestRenderComponents:

    @pytest.fixture
    def render_string(self):
        return jx.Catalog().render_string

    def test_literal_braces_are_not_interpreted_as_jinja(self, render_string):
        html = "<pre>body { color: red }</pre>\n<p>{{ not_a_variable }}</p>"

        result = render_components(html, {}, render_string=render_string)

        assert result.strip() == html

    def test_braces_survive_even_when_they_look_like_a_statement(self, render_string):
        html = "<pre>{% if x %}</pre>"

        result = render_components(html, {}, render_string=render_string)

        assert result.strip() == html


class TestUnterminatedTags:
    """Malformed input must be left alone rather than half-rewritten."""

    def test_an_opening_tag_that_never_closes(self):
        source = '<Card title="oops {% fill a %}'

        assert protect_fill_tags(source, IMPORTS) == (source, [])

    def test_a_body_that_never_closes(self):
        source = "<Card>{% fill a %}"

        assert protect_fill_tags(source, IMPORTS) == (source, [])

    def test_a_nested_tag_that_never_closes(self):
        source = '<Card>{% fill a %}<Card title="oops</Card>'
        result, fill_tags = protect_fill_tags(source, IMPORTS)

        assert fill_tags == []
        assert result == source

    def test_a_good_tag_after_a_broken_one_is_still_handled(self):
        source = "<Card>unclosed <Card>{% fill a %}</Card>"
        _, fill_tags = protect_fill_tags(source, IMPORTS)

        assert [tag for _, tag in fill_tags] == ["{% fill a %}"]
