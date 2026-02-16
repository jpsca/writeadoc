from pathlib import Path

import pytest

from writeadoc.main import Docs
from writeadoc.types import PageData


@pytest.fixture
def docs(tmp_root):
    """Create a minimal Docs instance for testing."""
    (tmp_root / "views" / "index.jinja").write_text("<h1>Home</h1>")
    (tmp_root / "views" / "search.jinja").write_text("<h1>Search</h1>")
    return Docs(
        str(tmp_root),
        pages=[],
        site={"name": "Test"},
    )


def _make_page(
    source: str,
    filepath: Path,
    url: str = "/docs/test/",
    content: str = "",
) -> PageData:
    return PageData(
        url=url,
        source=source,
        content=content,
        filepath=filepath,
        meta={"id": "test", "title": "Test"},
    )


class TestValidateLinks:

    def test_valid_link_to_existing_page(self, docs, capsys):
        """Links pointing to known page URLs should not produce warnings."""
        page1 = _make_page(
            source="See [other page](/docs/other/)",
            filepath=docs.content_dir / "test.md",
            url="/docs/test/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=docs.content_dir / "other.md",
            url="/docs/other/",
        )
        docs.site.pages = [page1, page2]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_broken_link_prints_warning(self, docs, capsys):
        """A link to a non-existent page should print a warning."""
        page = _make_page(
            source="See [missing](/docs/nonexistent/)",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "test.md:1" in output
        assert "broken link: /docs/nonexistent/" in output

    def test_external_links_are_skipped(self, docs, capsys):
        """External http/https/mailto/tel links should not be checked."""
        page = _make_page(
            source="\n".join([
                "Visit [example](https://example.com)",
                "Email [us](mailto:test@test.com)",
                "Call [us](tel:+1234567890)",
                "See [http](http://example.com)",
            ]),
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_anchor_only_links_are_skipped(self, docs, capsys):
        """Links that are just anchors (#section) should not be checked."""
        page = _make_page(
            source="See [section](#my-section)",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_link_with_anchor_checks_base_url(self, docs, capsys):
        """A link like /docs/other/#section should validate /docs/other/."""
        page1 = _make_page(
            source="See [other](/docs/other/#section)",
            filepath=docs.content_dir / "test.md",
            url="/docs/test/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=docs.content_dir / "other.md",
            url="/docs/other/",
        )
        docs.site.pages = [page1, page2]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_correct_line_number_reported(self, docs, capsys):
        """The warning should report the correct line number."""
        page = _make_page(
            source="Line one\nLine two\nSee [broken](/docs/nope/)\nLine four",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "test.md:3" in output

    def test_multiple_broken_links(self, docs, capsys):
        """Multiple broken links should each produce a warning."""
        page = _make_page(
            source="[a](/docs/aaa/)\n[b](/docs/bbb/)",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "test.md:1" in output
        assert "/docs/aaa/" in output
        assert "test.md:2" in output
        assert "/docs/bbb/" in output

    def test_link_to_existing_asset_file(self, docs, capsys):
        """Links to assets that exist in the assets dir should not warn."""
        asset_path = docs.assets_dir / "image.png"
        asset_path.write_text("fake image")

        page = _make_page(
            source="![img](/assets/image.png)",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_link_with_title_attribute(self, docs, capsys):
        """Links with a title attribute should extract the URL correctly."""
        asset_path = docs.assets_dir / "images" / "photo.jpg"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_text("fake image")

        page = _make_page(
            source='![alt](/assets/images/photo.jpg "My Photo Title")',
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_missing_asset_file(self, docs, capsys):
        """Links to assets that don't exist should warn."""
        page = _make_page(
            source="![img](/assets/missing.png)",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "test.md:1" in output
        assert "broken link: /assets/missing.png" in output

    def test_nested_asset_path(self, docs, capsys):
        """Links to nested assets should resolve against the assets dir."""
        nested = docs.assets_dir / "css" / "style.css"
        nested.parent.mkdir(parents=True, exist_ok=True)
        nested.write_text("body {}")

        page = _make_page(
            source="[css](/assets/css/style.css)",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_relative_link_resolved_against_page_url(self, docs, capsys):
        """Relative links should be resolved against the page's URL."""
        page1 = _make_page(
            source="See [sibling](sibling/)",
            filepath=docs.content_dir / "start" / "intro.md",
            url="/docs/start/intro/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=docs.content_dir / "start" / "sibling.md",
            url="/docs/start/intro/sibling/",
        )
        docs.site.pages = [page1, page2]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_broken_relative_link(self, docs, capsys):
        """A relative link that doesn't resolve should warn."""
        page = _make_page(
            source="See [missing](nope)",
            filepath=docs.content_dir / "test.md",
            url="/docs/test/",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link: nope" in output

    def test_warning_shows_path_relative_to_content_dir(self, docs, capsys):
        """Warnings should show the full path relative to content_dir."""
        page = _make_page(
            source="See [broken](/docs/nope/)",
            filepath=docs.content_dir / "guide" / "start" / "intro.md",
            url="/docs/guide/start/intro/",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "guide/start/intro.md:1" in output

    def test_pages_without_source_are_skipped(self, docs, capsys):
        """Pages with no source (template-only) should be skipped."""
        page = PageData(
            url="/",
            meta={"id": "index", "title": "Home", "view": "index.jinja"},
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken link" not in output

    def test_link_warnings_header_printed_once(self, docs, capsys):
        """The 'Link warnings:' header should only be printed once."""
        page = _make_page(
            source="[a](/docs/aaa/)\n[b](/docs/bbb/)",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert output.count("WARNING:") == 1

    def test_no_warnings_prints_nothing(self, docs, capsys):
        """When all links are valid, nothing should be printed."""
        page = _make_page(
            source="Just text, no links here.",
            filepath=docs.content_dir / "test.md",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert output == ""


class TestValidateAnchors:

    def test_valid_anchor_link(self, docs, capsys):
        """An anchor link pointing to an existing ID should not warn."""
        page = _make_page(
            source="See [section](#my-heading)",
            filepath=docs.content_dir / "test.md",
            content='<h2 id="my-heading">My Heading</h2><p>Content</p>',
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken anchor" not in output

    def test_broken_anchor_link(self, docs, capsys):
        """An anchor link pointing to a non-existent ID should warn."""
        page = _make_page(
            source="See [section](#nonexistent)",
            filepath=docs.content_dir / "test.md",
            content='<h2 id="my-heading">My Heading</h2>',
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "test.md:1" in output
        assert "broken anchor: #nonexistent" in output

    def test_anchor_correct_line_number(self, docs, capsys):
        """The warning should report the correct line for broken anchors."""
        page = _make_page(
            source="Line one\n\nLine three [link](#nope)\n",
            filepath=docs.content_dir / "intro.md",
            content='<h1 id="intro">Intro</h1>',
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "intro.md:3" in output
        assert "broken anchor: #nope" in output

    def test_multiple_ids_in_content(self, docs, capsys):
        """Anchors should be checked against all IDs in the page content."""
        html = (
            '<h1 id="intro">Intro</h1>'
            '<h2 id="setup">Setup</h2>'
            '<div id="example">Example</div>'
        )
        page = _make_page(
            source="[a](#intro) [b](#setup) [c](#example)",
            filepath=docs.content_dir / "test.md",
            content=html,
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken anchor" not in output

    def test_mixed_valid_and_broken_anchors(self, docs, capsys):
        """Only broken anchors should produce warnings."""
        html = '<h1 id="intro">Intro</h1><h2 id="setup">Setup</h2>'
        page = _make_page(
            source="[a](#intro)\n[b](#missing)\n[c](#setup)",
            filepath=docs.content_dir / "test.md",
            content=html,
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "test.md:2" in output
        assert "broken anchor: #missing" in output
        assert "#intro" not in output
        assert "#setup" not in output

    def test_anchor_with_single_quotes(self, docs, capsys):
        """IDs using single quotes in HTML should be detected."""
        page = _make_page(
            source="See [section](#my-id)",
            filepath=docs.content_dir / "test.md",
            content="<h2 id='my-id'>Heading</h2>",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken anchor" not in output

    def test_page_without_content_skips_anchor_check(self, docs, capsys):
        """Pages with no rendered content should skip anchor validation."""
        page = _make_page(
            source="See [section](#anything)",
            filepath=docs.content_dir / "test.md",
            content="",
        )
        docs.site.pages = [page]

        docs._validate_links()

        output = capsys.readouterr().out
        assert "broken anchor" not in output
