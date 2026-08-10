import pytest

from writeadoc.exceptions import InvalidFrontMatter
from writeadoc.frontmatter import dict_to_yaml, extract_metadata, render_metadata


def test_extract_metadata_preserves_leading_list_marker():
    source = """
---
title: Test
---
- first
- second
""".strip()

    body, meta = extract_metadata(source)

    assert meta == {"title": "Test"}
    assert body == "- first\n- second"


def test_extract_metadata_preserves_leading_thematic_break():
    source = """
---
title: Test
---
---
body
""".strip()

    body, meta = extract_metadata(source)

    assert meta == {"title": "Test"}
    assert body == "---\nbody"


class TestExtractMetadata:

    def test_a_source_without_front_matter_is_returned_whole(self):
        source = "# Title\n\nBody."

        assert extract_metadata(source) == (source, {})

    def test_an_empty_source(self):
        assert extract_metadata("") == ("", {})

    def test_the_body_is_stripped(self):
        body, _ = extract_metadata("---\ntitle: T\n---\n\n\nBody.\n\n")

        assert body == "Body."

    def test_an_unclosed_front_matter_is_an_error(self):
        with pytest.raises(InvalidFrontMatter, match="Missing closing"):
            extract_metadata("---\ntitle: T\n\nBody.")

    def test_invalid_yaml_is_an_error(self):
        with pytest.raises(InvalidFrontMatter):
            extract_metadata("---\ntitle: [unclosed\n---\n\nBody.")

    def test_front_matter_that_is_not_a_mapping_yields_no_metadata(self):
        body, meta = extract_metadata("---\n- one\n- two\n---\n\nBody.")

        assert meta == {}
        assert body == "Body."

    def test_the_error_quotes_a_truncated_source(self):
        source = "---\ntitle: T\n" + "x" * 900

        with pytest.raises(InvalidFrontMatter) as caught:
            extract_metadata(source)

        quoted = caught.value.args[0]
        assert len(quoted) == 400
        assert quoted.endswith("...")


class TestRenderMetadata:

    def test_no_metadata_renders_nothing(self):
        assert render_metadata({}) == ""

    def test_keyword_arguments_are_merged_in(self):
        rendered = render_metadata({"title": "T"}, url="/docs/t/")

        assert rendered == "---\ntitle: T\nurl: /docs/t/\n---"

    def test_keyword_arguments_win(self):
        assert render_metadata({"url": "/old/"}, url="/new/") == "---\nurl: /new/\n---"


class TestValueFormatting:
    """The reason this is not `strictyaml.as_document().as_yaml()`, which renders
    booleans as `yes`/`no`, quotes with `'`, and raises on `None`.
    """

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, "null"),
            (True, "true"),
            (False, "false"),
            (3, "3"),
            (1.5, "1.5"),
            ("plain", "plain"),
        ],
    )
    def test_scalars(self, value, expected):
        assert dict_to_yaml({"k": value}) == f"k: {expected}"

    @pytest.mark.parametrize(
        "value",
        ["a: b", "a#b", "a{b", "a[b", "a,b", "it's", 'say "hi"', "back\\slash"],
    )
    def test_strings_needing_quotes_are_quoted(self, value):
        rendered = dict_to_yaml({"k": value})

        assert rendered.startswith('k: "')
        assert rendered.endswith('"')

    def test_double_quotes_are_escaped(self):
        assert dict_to_yaml({"k": 'say "hi"'}) == 'k: "say \\"hi\\""'


class TestDictToYaml:

    def test_an_empty_mapping(self):
        assert dict_to_yaml({}) == "{}"

    def test_a_nested_mapping_is_indented(self):
        assert dict_to_yaml({"imports": {"Card": "card.jx"}}) == (
            "imports:\n  Card: card.jx"
        )

    def test_an_empty_nested_mapping(self):
        assert dict_to_yaml({"k": {}}) == "k: {}"

    def test_a_list(self):
        assert dict_to_yaml({"tags": ["a", "b"]}) == "tags:\n  - a\n  - b"

    def test_an_empty_list(self):
        assert dict_to_yaml({"tags": []}) == "tags: []"

    def test_a_list_of_mappings_keeps_its_keys(self):
        rendered = dict_to_yaml({"authors": [{"name": "Ann"}, {"name": "Bo"}]})

        assert rendered == "authors:\n  -\n    name: Ann\n  -\n    name: Bo"

    def test_a_list_of_mappings_survives_a_round_trip(self):
        meta = {"authors": [{"name": "Ann", "email": "a@x.com"}]}

        _, back = extract_metadata(f"{render_metadata(meta)}\nBody.")

        assert back == meta


def test_a_value_of_another_type_falls_back_to_its_string_form():
    from datetime import date

    assert dict_to_yaml({"date": date(2024, 1, 31)}) == "date: 2024-01-31"
