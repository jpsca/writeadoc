"""The starter theme that `writeadoc init` copies into a new project.

Nothing else builds it, so a view that only breaks once a documented feature is
enabled, such as versions or languages, would go unnoticed.
"""

import shutil
from pathlib import Path

import pytest

import writeadoc
from writeadoc import Docs


BLUEPRINT = Path(writeadoc.__file__).parent / "blueprint"

SITE = {
    "name": "Project",
    "base_url": "https://project.example.com",
    "description": "Description of your project",
    "source_code": "https://github.com/example/project/",
}


@pytest.fixture
def build_blueprint(tmp_path):
    """Build a project made of the blueprint views, and return its build folder."""

    def build(*, prefix: str = "", variants: tuple[str, ...] = ()) -> Path:
        root = tmp_path / f"p{prefix}{'-'.join(variants)}"
        shutil.copytree(BLUEPRINT / "views", root / "views")
        shutil.copytree(BLUEPRINT / "content", root / "content")
        (root / "assets").mkdir()

        built_variants = {}
        for name in variants:
            (root / "content" / name).mkdir()
            shutil.copy(
                root / "content" / "welcome.md",
                root / "content" / name / "welcome.md",
            )
            built_variants[name] = Docs(
                root, pages=["welcome.md"], site={**SITE, "lang": name}
            )

        docs = Docs(root, pages=["welcome.md"], site=SITE, variants=built_variants)
        docs._set_build_target(build_dir=root / "out", prefix=prefix)
        docs.build(devmode=True, boring=True)
        return docs.build_target.out_dir

    return build


def test_the_starter_theme_builds(build_blueprint):
    out = build_blueprint()

    assert (out / "index.html").exists()
    assert (out / "docs" / "welcome" / "index.html").exists()
    assert (out / "search" / "index.html").exists()
    assert (out / "robots.txt").exists()
    assert (out / "sitemap.xml").exists()


def test_robots_disallows_the_search_page(build_blueprint):
    robots = (build_blueprint() / "robots.txt").read_text()

    assert "Disallow: /search/" in robots
    assert "Sitemap: https://project.example.com/sitemap.xml" in robots


def test_robots_follows_the_prefix(build_blueprint):
    """An archived build serves the search page under the version prefix."""
    robots = (build_blueprint(prefix="2.5") / "robots.txt").read_text()

    assert "Disallow: /2.5/search/" in robots
    assert "Disallow: /search/\n" not in robots


def test_robots_covers_every_variant(build_blueprint):
    out = build_blueprint(prefix="2.5", variants=("es", "it"))
    robots = (out / "robots.txt").read_text()

    assert "Disallow: /2.5/search/" in robots
    assert "Disallow: /2.5/es/search/" in robots
    assert "Disallow: /2.5/it/search/" in robots


def test_variants_are_built_under_their_own_prefix(build_blueprint):
    out = build_blueprint(prefix="2.5", variants=("es",))

    assert (out / "es" / "docs" / "welcome" / "index.html").exists()


def test_a_404_page_is_generated(build_blueprint):
    """`_render_extra` renders `not_found.html` only if the view exists."""
    not_found = (build_blueprint() / "not_found.html").read_text()

    assert "Page not found" in not_found
    assert 'href="/"' in not_found


def test_the_404_page_is_translated(build_blueprint, tmp_path):
    root = tmp_path / "es"
    shutil.copytree(BLUEPRINT / "views", root / "views")
    shutil.copytree(BLUEPRINT / "content", root / "content")
    (root / "assets").mkdir()

    docs = Docs(root, pages=["welcome.md"], site={**SITE, "lang": "es"})
    docs._set_build_target(build_dir=root / "out", prefix="")
    docs.build(devmode=True, boring=True)

    assert "Página no encontrada" in (root / "out" / "not_found.html").read_text()


def test_the_favicons_offer_a_png_fallback(build_blueprint):
    html = (build_blueprint() / "index.html").read_text()

    assert '<link rel="icon" type="image/svg+xml" href="/assets/images/favicon.svg" />' in html
    assert 'type="image/png" sizes="192x192" href="/assets/images/favicon.png"' in html


def test_the_body_starts_with_no_js_and_an_anchor(build_blueprint):
    html = (build_blueprint() / "index.html").read_text()

    assert 'no-js" id="top"' in html
    assert "classList.remove('no-js')" in html


def test_the_page_nav_is_hidden_on_the_home_page(build_blueprint):
    out = build_blueprint()

    assert "page__nav" not in (out / "index.html").read_text()
    assert "page__nav" in (out / "docs" / "welcome" / "index.html").read_text()


def test_the_page_nav_is_hidden_on_a_prefixed_home_page(build_blueprint):
    """The home of a prefixed build is `/2.5/`, not `/`."""
    out = build_blueprint(prefix="2.5")

    assert "page__nav" not in (out / "index.html").read_text()
    assert "page__nav" in (out / "docs" / "welcome" / "index.html").read_text()
