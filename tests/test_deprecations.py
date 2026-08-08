"""The temporary shims for `docs.prefix` and `docs.build_dir`.

Both moved onto `docs.build_target`, exposed to the views as `build`. Delete
this file, and the properties in `main.py`, when the shims are removed in 0.29.
"""

from pathlib import Path

import pytest

from writeadoc import Docs


@pytest.fixture
def docs(tmp_root):
    (tmp_root / "views" / "index.jx").write_text("<h1>Home</h1>")
    (tmp_root / "content" / "one.md").write_text("---\ntitle: One\n---\n\nHi.")
    return Docs(tmp_root, pages=["one.md"], prefix="v2", site={"name": "Test"})


class TestReading:

    def test_prefix_warns_and_returns_the_build_prefix(self, docs):
        with pytest.warns(FutureWarning, match="`docs.prefix` is deprecated"):
            value = docs.prefix

        assert value == docs.build_target.prefix == "v2"

    def test_build_dir_warns_and_returns_the_build_dir(self, docs):
        with pytest.warns(FutureWarning, match="`docs.build_dir` is deprecated"):
            value = docs.build_dir

        assert value == docs.build_target.dir

    def test_the_warning_names_the_replacement(self, docs):
        with pytest.warns(FutureWarning) as caught:
            docs.build_dir  # noqa: B018

        message = str(caught[0].message)
        assert "build.dir" in message
        assert "docs.build_target.dir" in message
        assert "0.29" in message


class TestWriting:

    def test_setting_build_dir_moves_the_target(self, docs, tmp_path):
        target = tmp_path / "elsewhere"

        with pytest.warns(FutureWarning):
            docs.build_dir = target

        assert docs.build_target.dir == target
        assert docs.build_target.prefix == "v2"

    def test_setting_prefix_moves_the_target(self, docs):
        with pytest.warns(FutureWarning):
            docs.prefix = "v3"

        assert docs.build_target.prefix == "v3"

    def test_setting_still_propagates_to_variants(self, tmp_root, tmp_path):
        (tmp_root / "views" / "index.jx").write_text("<h1>Home</h1>")
        (tmp_root / "content" / "es").mkdir()
        (tmp_root / "content" / "one.md").write_text("---\ntitle: One\n---\n\nHi.")
        (tmp_root / "content" / "es" / "one.md").write_text("---\ntitle: Uno\n---\n\nHola.")

        variant = Docs(tmp_root, pages=["one.md"], site={"lang": "es"})
        docs = Docs(tmp_root, pages=["one.md"], variants={"es": variant})

        with pytest.warns(FutureWarning):
            docs.prefix = "v2"

        assert variant.build_target.prefix == "v2/es"
        assert docs.build_target.variants["es"].prefix == "v2/es"


class TestInViews:

    def test_a_view_reading_docs_prefix_still_renders(self, docs):
        with pytest.warns(FutureWarning):
            rendered = docs.catalog.render_string("[{{ docs.prefix }}]")

        assert str(rendered) == "[v2]"

    def test_the_replacement_does_not_warn(self, docs, recwarn):
        rendered = docs.catalog.render_string("[{{ build.prefix }}]")

        assert str(rendered) == "[v2]"
        assert [w for w in recwarn if issubclass(w.category, FutureWarning)] == []


def test_the_build_still_uses_the_new_api(docs, tmp_path, recwarn):
    """The library itself must not trip its own deprecation."""
    docs._set_build_target(build_dir=tmp_path / "out", prefix="v2")
    docs.build(devmode=True, boring=True)

    assert (tmp_path / "out" / "v2" / "docs" / "one" / "index.html").exists()
    assert [w for w in recwarn if issubclass(w.category, FutureWarning)] == []


def test_build_dir_accepts_a_path(docs, tmp_path):
    with pytest.warns(FutureWarning):
        docs.build_dir = tmp_path

    assert isinstance(docs.build_target.dir, Path)
