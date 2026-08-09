"""Every page also publishes the markdown it was built from, as `<url>.md`."""

import pytest

from writeadoc import Docs


@pytest.fixture
def build(tmp_root):
    (tmp_root / "views" / "index.jx").write_text("<h1>{{ site.name }}</h1>")
    (tmp_root / "content" / "start").mkdir()
    (tmp_root / "content" / "one.md").write_text(
        "---\ntitle: One\n---\n\nHi, see [two](/docs/start/two/)."
    )
    (tmp_root / "content" / "start" / "two.md").write_text(
        "---\ntitle: Two\n---\n\nThe end."
    )

    def run(*, prefix: str = "", with_index_md: bool = False):
        if with_index_md:
            (tmp_root / "content" / "index.md").write_text(
                "---\ntitle: Home\n---\n\nWelcome."
            )
        docs = Docs(tmp_root, pages=["one.md", "start/two.md"], prefix=prefix)
        docs._set_build_target(build_dir=tmp_root / "out", prefix=prefix)
        docs.build(devmode=True, boring=True)
        return docs.build_target.dir

    return run


def test_a_page_publishes_its_markdown_beside_it(build):
    out = build()

    assert (out / "docs" / "one" / "index.html").exists()
    assert (out / "docs" / "one.md").exists()


def test_nested_pages_keep_their_folders(build):
    out = build()

    assert (out / "docs" / "start" / "two.md").exists()


def test_the_markdown_carries_the_front_matter_and_the_body(build):
    source = (build() / "docs" / "one.md").read_text()

    assert source.startswith("---\n")
    assert "title: One" in source
    assert "url: /docs/one/" in source
    assert source.rstrip().endswith("Hi, see [two](/docs/start/two/).")


def test_the_home_page_publishes_index_md(build):
    out = build(with_index_md=True)

    assert (out / "index.md").read_text().rstrip().endswith("Welcome.")


def test_a_page_without_markdown_publishes_nothing(build):
    """The home rendered straight from `index.jx` has no source behind it."""
    out = build()

    assert not (out / "index.md").exists()
    assert not (out / "search.md").exists()


class TestWithAPrefix:

    def test_the_markdown_follows_the_prefix(self, build):
        out = build(prefix="v2")

        assert (out / "v2" / "docs" / "one.md").exists()
        assert not (out / "docs" / "one.md").exists()

    def test_the_home_markdown_stays_inside_the_prefix(self, build):
        out = build(prefix="v2", with_index_md=True)

        assert (out / "v2" / "index.md").exists()
        assert not (out / "v2.md").exists()


def test_the_release_build_publishes_them_too(tmp_root):
    """`cli_build` is the deploy path, and takes a different branch than devmode."""
    (tmp_root / "views" / "index.jx").write_text("<h1>{{ site.name }}</h1>")
    (tmp_root / "content" / "one.md").write_text("---\ntitle: One\n---\n\nHi.")

    docs = Docs(tmp_root, pages=["one.md"])
    docs.cli_build(archive=False, boring=True)

    assert (tmp_root / "build" / "docs" / "one.md").read_text().rstrip().endswith("Hi.")


def test_the_archive_build_publishes_them_too(tmp_root):
    (tmp_root / "views" / "index.jx").write_text("<h1>{{ site.name }}</h1>")
    (tmp_root / "content" / "one.md").write_text("---\ntitle: One\n---\n\nHi.")

    docs = Docs(tmp_root, pages=["one.md"], site={"version": "2.5"})
    docs.cli_build(archive=True, boring=True)

    assert (tmp_root / "archive" / "2.5" / "docs" / "one.md").exists()
