from dataclasses import dataclass
from pathlib import Path

import pytest

from writeadoc.links import LinkWarning, get_prefixed_folders, validate_links
from writeadoc.main import Docs
from writeadoc.types import PageData


@dataclass
class Project:
    """The folder layout `validate_links` reads from, plus a call shortcut."""

    root: Path

    @property
    def content_dir(self) -> Path:
        return self.root / "content"

    @property
    def assets_dir(self) -> Path:
        return self.root / "assets"

    def check(
        self,
        pages: list[PageData],
        *,
        prefix: str = "",
        is_main: bool = True,
    ) -> list[LinkWarning]:
        return validate_links(
            pages,
            content_root=self.content_dir,
            assets_dir=self.assets_dir,
            build_dir=self.root / "build",
            root_dir=self.root,
            prefix=prefix,
            is_main=is_main,
        )


@pytest.fixture
def project(tmp_path):
    (tmp_path / "content").mkdir()
    (tmp_path / "assets").mkdir()
    return Project(tmp_path)


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

    def test_valid_link_to_existing_page(self, project):
        """Links pointing to known page URLs should not produce warnings."""
        page1 = _make_page(
            source="See [other page](/docs/other/)",
            filepath=project.content_dir / "test.md",
            url="/docs/test/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=project.content_dir / "other.md",
            url="/docs/other/",
        )

        assert project.check([page1, page2]) == []

    def test_broken_link_is_reported(self, project):
        """A link to a non-existent page should produce a warning."""
        page = _make_page(
            source="See [missing](/docs/nonexistent/)",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == [
            LinkWarning("test.md", 1, "broken link: /docs/nonexistent/")
        ]

    def test_external_links_are_skipped(self, project):
        """External http/https/mailto/tel links should not be checked."""
        page = _make_page(
            source="\n".join([
                "Visit [example](https://example.com)",
                "Email [us](mailto:test@test.com)",
                "Call [us](tel:+1234567890)",
                "See [http](http://example.com)",
            ]),
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == []

    def test_llms_txt_links_are_skipped(self, project):
        """References to the generated llms.txt should not be checked."""
        page = _make_page(
            source="See [the index](/llms.txt)",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == []

    def test_anchor_only_links_are_skipped(self, project):
        """Links that are just anchors (#section) should not be checked."""
        page = _make_page(
            source="See [section](#my-section)",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == []

    def test_link_with_anchor_checks_base_url(self, project):
        """A link like /docs/other/#section should validate /docs/other/."""
        page1 = _make_page(
            source="See [other](/docs/other/#section)",
            filepath=project.content_dir / "test.md",
            url="/docs/test/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=project.content_dir / "other.md",
            url="/docs/other/",
        )

        assert project.check([page1, page2]) == []

    def test_correct_line_number_reported(self, project):
        """The warning should report the correct line number."""
        page = _make_page(
            source="Line one\nLine two\nSee [broken](/docs/nope/)\nLine four",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == [
            LinkWarning("test.md", 3, "broken link: /docs/nope/")
        ]

    def test_multiple_broken_links(self, project):
        """Multiple broken links should each produce a warning."""
        page = _make_page(
            source="[a](/docs/aaa/)\n[b](/docs/bbb/)",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == [
            LinkWarning("test.md", 1, "broken link: /docs/aaa/"),
            LinkWarning("test.md", 2, "broken link: /docs/bbb/"),
        ]

    def test_link_to_existing_asset_file(self, project):
        """Links to assets that exist in the assets dir should not warn."""
        (project.assets_dir / "image.png").write_text("fake image")

        page = _make_page(
            source="![img](/assets/image.png)",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == []

    def test_link_with_title_attribute(self, project):
        """Links with a title attribute should extract the URL correctly."""
        asset_path = project.assets_dir / "images" / "photo.jpg"
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        asset_path.write_text("fake image")

        page = _make_page(
            source='![alt](/assets/images/photo.jpg "My Photo Title")',
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == []

    def test_missing_asset_file(self, project):
        """Links to assets that don't exist should warn."""
        page = _make_page(
            source="![img](/assets/missing.png)",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == [
            LinkWarning("test.md", 1, "broken link: /assets/missing.png")
        ]

    def test_nested_asset_path(self, project):
        """Links to nested assets should resolve against the assets dir."""
        nested = project.assets_dir / "css" / "style.css"
        nested.parent.mkdir(parents=True, exist_ok=True)
        nested.write_text("body {}")

        page = _make_page(
            source="[css](/assets/css/style.css)",
            filepath=project.content_dir / "test.md",
        )

        assert project.check([page]) == []

    def test_relative_link_resolved_against_page_url(self, project):
        """Relative links should be resolved against the page's URL."""
        page1 = _make_page(
            source="See [sibling](sibling/)",
            filepath=project.content_dir / "start" / "intro.md",
            url="/docs/start/intro/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=project.content_dir / "start" / "sibling.md",
            url="/docs/start/intro/sibling/",
        )

        assert project.check([page1, page2]) == []

    def test_parent_relative_link_resolved_against_page_url(self, project):
        """Parent relative links should be normalized before validation."""
        page1 = _make_page(
            source="See [usage](../usage/)",
            filepath=project.content_dir / "start" / "intro.md",
            url="/docs/start/intro/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=project.content_dir / "start" / "usage.md",
            url="/docs/start/usage/",
        )

        assert project.check([page1, page2]) == []

    def test_broken_relative_link(self, project):
        """A relative link that doesn't resolve should warn."""
        page = _make_page(
            source="See [missing](nope)",
            filepath=project.content_dir / "test.md",
            url="/docs/test/",
        )

        assert project.check([page]) == [
            LinkWarning("test.md", 1, "broken link: nope")
        ]

    def test_warning_shows_path_relative_to_content_dir(self, project):
        """Warnings should show the full path relative to the content folder."""
        page = _make_page(
            source="See [broken](/docs/nope/)",
            filepath=project.content_dir / "guide" / "start" / "intro.md",
            url="/docs/guide/start/intro/",
        )

        warnings = project.check([page])

        assert [w.filename for w in warnings] == ["guide/start/intro.md"]

    def test_pages_without_source_are_skipped(self, project):
        """Pages with no source (template-only) should be skipped."""
        page = PageData(
            url="/",
            meta={"id": "index", "title": "Home", "view": "index.jx"},
        )

        assert project.check([page]) == []


class TestValidateLinksWithPrefix:
    """Markdown sources reference unprefixed paths, so a prefixed site has to
    apply the prefix before looking the URL up, mirroring `_add_prefix_to_urls`.
    """

    def test_page_link_gets_the_prefix(self, project):
        page1 = _make_page(
            source="See [other](/docs/other/)",
            filepath=project.content_dir / "test.md",
            url="/v2/docs/test/",
        )
        page2 = _make_page(
            source="Hello",
            filepath=project.content_dir / "other.md",
            url="/v2/docs/other/",
        )

        assert project.check([page1, page2], prefix="v2") == []

    def test_broken_page_link_is_reported_with_its_raw_url(self, project):
        """The message quotes the source URL, not the prefixed one."""
        page = _make_page(
            source="See [other](/docs/other/)",
            filepath=project.content_dir / "test.md",
            url="/v2/docs/test/",
        )

        assert project.check([page], prefix="v2") == [
            LinkWarning("test.md", 1, "broken link: /docs/other/")
        ]

    def test_asset_link_resolves_against_the_assets_folder(self, project):
        """Assets are looked up in their source folder, prefixed or not."""
        (project.assets_dir / "image.png").write_text("fake image")
        page = _make_page(
            source="![ok](/assets/image.png)\n![no](/assets/missing.png)",
            filepath=project.content_dir / "test.md",
            url="/v2/docs/test/",
        )

        assert project.check([page], prefix="v2") == [
            LinkWarning("test.md", 2, "broken link: /assets/missing.png")
        ]

    @pytest.mark.parametrize(
        ("prefix", "is_main", "expected"),
        [
            ("", True, ()),
            ("", False, ()),
            ("v2", True, ("docs", "assets", "search")),
            ("v2/es", False, ("docs", "search")),
        ],
    )
    def test_prefixed_folders(self, prefix, is_main, expected):
        """Variants share the main site's assets folder, so they don't prefix it.

        This only affects `_add_prefix_to_urls`: `validate_links` looks assets up
        in their source folder either way, so the distinction is invisible here.
        """
        assert get_prefixed_folders(prefix=prefix, is_main=is_main) == expected


class TestValidateAnchors:

    def test_valid_anchor_link(self, project):
        """An anchor link pointing to an existing ID should not warn."""
        page = _make_page(
            source="See [section](#my-heading)",
            filepath=project.content_dir / "test.md",
            content='<h2 id="my-heading">My Heading</h2><p>Content</p>',
        )

        assert project.check([page]) == []

    def test_broken_anchor_link(self, project):
        """An anchor link pointing to a non-existent ID should warn."""
        page = _make_page(
            source="See [section](#nonexistent)",
            filepath=project.content_dir / "test.md",
            content='<h2 id="my-heading">My Heading</h2>',
        )

        assert project.check([page]) == [
            LinkWarning("test.md", 1, "broken anchor: #nonexistent")
        ]

    def test_anchor_correct_line_number(self, project):
        """The warning should report the correct line for broken anchors."""
        page = _make_page(
            source="Line one\n\nLine three [link](#nope)\n",
            filepath=project.content_dir / "intro.md",
            content='<h1 id="intro">Intro</h1>',
        )

        assert project.check([page]) == [
            LinkWarning("intro.md", 3, "broken anchor: #nope")
        ]

    def test_multiple_ids_in_content(self, project):
        """Anchors should be checked against all IDs in the page content."""
        html = (
            '<h1 id="intro">Intro</h1>'
            '<h2 id="setup">Setup</h2>'
            '<div id="example">Example</div>'
        )
        page = _make_page(
            source="[a](#intro) [b](#setup) [c](#example)",
            filepath=project.content_dir / "test.md",
            content=html,
        )

        assert project.check([page]) == []

    def test_mixed_valid_and_broken_anchors(self, project):
        """Only broken anchors should produce warnings."""
        html = '<h1 id="intro">Intro</h1><h2 id="setup">Setup</h2>'
        page = _make_page(
            source="[a](#intro)\n[b](#missing)\n[c](#setup)",
            filepath=project.content_dir / "test.md",
            content=html,
        )

        assert project.check([page]) == [
            LinkWarning("test.md", 2, "broken anchor: #missing")
        ]

    def test_anchor_with_single_quotes(self, project):
        """IDs using single quotes in HTML should be detected."""
        page = _make_page(
            source="See [section](#my-id)",
            filepath=project.content_dir / "test.md",
            content="<h2 id='my-id'>Heading</h2>",
        )

        assert project.check([page]) == []

    def test_page_without_content_skips_anchor_check(self, project):
        """Pages with no rendered content should skip anchor validation."""
        page = _make_page(
            source="See [section](#anything)",
            filepath=project.content_dir / "test.md",
            content="",
        )

        assert project.check([page]) == []


class TestWarningsOutput:
    """`Docs._validate_links` is the thin layer that prints the warnings."""

    @pytest.fixture
    def docs(self, tmp_root):
        (tmp_root / "views" / "index.jx").write_text("<h1>Home</h1>")
        (tmp_root / "views" / "search.jx").write_text("<h1>Search</h1>")
        return Docs(str(tmp_root), pages=[], site={"name": "Test"})

    def test_header_printed_once_for_several_warnings(self, docs, capsys):
        docs.site.pages = [
            _make_page(
                source="[a](/docs/aaa/)\n[b](/docs/bbb/)",
                filepath=docs.content_dir / "test.md",
            )
        ]

        docs._validate_links()

        output = capsys.readouterr().out
        assert output.count("WARNING:") == 1
        assert "  test.md:1 - broken link: /docs/aaa/" in output
        assert "  test.md:2 - broken link: /docs/bbb/" in output

    def test_nothing_printed_when_all_links_are_valid(self, docs, capsys):
        docs.site.pages = [
            _make_page(
                source="Just text, no links here.",
                filepath=docs.content_dir / "test.md",
            )
        ]

        docs._validate_links()

        assert capsys.readouterr().out == ""
