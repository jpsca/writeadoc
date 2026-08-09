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


class TestLinksUnderAPrefix:
    """The markdown has to stay inside its own prefix, like the HTML does."""

    @pytest.fixture
    def project(self, tmp_root):
        (tmp_root / "views" / "index.jx").write_text("<h1>{{ site.name }}</h1>")
        (tmp_root / "content" / "one.md").write_text(
            "---\ntitle: One\n---\n\nSee [two](/docs/two/) and ![a](/assets/a.png)."
        )
        (tmp_root / "content" / "two.md").write_text("---\ntitle: Two\n---\n\nEnd.")
        (tmp_root / "assets" / "a.png").write_text("x")
        return tmp_root

    def _one_md(self, docs) -> str:
        return (docs.build_target.out_dir / "docs" / "one.md").read_text()

    def test_a_prefixed_build_rewrites_them(self, project):
        docs = Docs(project, pages=["one.md", "two.md"], prefix="v2")
        docs._set_build_target(build_dir=project / "out", prefix="v2")
        docs.build(devmode=True, boring=True)

        assert "[two](/v2/docs/two/)" in self._one_md(docs)
        assert "![a](/v2/assets/a.png)" in self._one_md(docs)

    def test_an_archived_build_keeps_the_source_links(self, project):
        docs = Docs(project, pages=["one.md", "two.md"], site={"version": "2.5"})
        docs.cli_build(archive=True, boring=True)

        assert "[two](/docs/two/)" in self._one_md(docs)
        assert "![a](/assets/a.png)" in self._one_md(docs)

    def test_an_unprefixed_build_leaves_them_alone(self, project):
        docs = Docs(project, pages=["one.md", "two.md"])
        docs._set_build_target(build_dir=project / "out", prefix="")
        docs.build(devmode=True, boring=True)

        assert "[two](/docs/two/)" in self._one_md(docs)

    def test_a_variant_does_not_prefix_the_shared_assets(self, project):
        """Variants share the main site's assets folder, as in the HTML."""
        (project / "content" / "es").mkdir()
        for name in ("one.md", "two.md"):
            (project / "content" / name).rename(project / "content" / "es" / name)
            (project / "content" / name).write_text(f"---\ntitle: {name}\n---\n\nx")

        variant = Docs(project, pages=["one.md", "two.md"], site={"lang": "es"})
        docs = Docs(project, pages=["one.md", "two.md"], variants={"es": variant})
        docs._set_build_target(build_dir=project / "out", prefix="")
        docs.build(devmode=True, boring=True)

        source = (variant.build_target.out_dir / "docs" / "one.md").read_text()
        assert "[two](/es/docs/two/)" in source
        assert "![a](/assets/a.png)" in source


def test_an_archived_build_marks_its_variants_archived_too(tmp_root):
    """`site.archived` drives the banner as well as the markdown links."""
    (tmp_root / "views" / "index.jx").write_text("<h1>{{ site.name }}</h1>")
    (tmp_root / "content" / "es").mkdir()
    (tmp_root / "content" / "one.md").write_text("---\ntitle: One\n---\n\nx")
    (tmp_root / "content" / "es" / "one.md").write_text("---\ntitle: Uno\n---\n\nx")

    variant = Docs(tmp_root, pages=["one.md"], site={"lang": "es"})
    docs = Docs(tmp_root, pages=["one.md"], site={"version": "2.5"}, variants={"es": variant})
    docs.cli_build(archive=True, boring=True)

    assert docs.site.archived is True
    assert variant.site.archived is True


def test_links_inside_a_code_block_are_examples_not_links(tmp_root):
    """The docs show markdown snippets; prefixing those would corrupt them."""
    (tmp_root / "views" / "index.jx").write_text("<h1>{{ site.name }}</h1>")
    (tmp_root / "content" / "one.md").write_text(
        "---\ntitle: One\n---\n\n"
        "A real link to [two](/docs/two/).\n\n"
        "```markdown\n"
        "![alt](/assets/images/image.png)\n"
        "[example](/docs/other/)\n"
        "```\n\n"
        "Another real one: [two again](/docs/two/).\n"
    )
    (tmp_root / "content" / "two.md").write_text("---\ntitle: Two\n---\n\nEnd.")

    docs = Docs(tmp_root, pages=["one.md", "two.md"], prefix="v2")
    docs._set_build_target(build_dir=tmp_root / "out", prefix="v2")
    docs.build(devmode=True, boring=True)

    source = (docs.build_target.out_dir / "docs" / "one.md").read_text()

    assert source.count("[two](/v2/docs/two/)") == 1
    assert "[two again](/v2/docs/two/)" in source
    assert "![alt](/assets/images/image.png)" in source
    assert "[example](/docs/other/)" in source
