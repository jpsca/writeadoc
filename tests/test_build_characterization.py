"""Characterization tests for the build pipeline.

These tests do not assert that the build output is *correct*; they assert that it
does not *change*. Their purpose is to be a safety net while `Docs.build()` and
its helpers are refactored: build the same projects before and after a change and
compare a manifest of every generated file.

Each case stores a golden manifest in `tests/golden/`, one `sha256  path` line per
generated file. When a change to the build pipeline is intentional (or the `docs/`
content is edited), regenerate them and review the diff:

    WRITEADOC_UPDATE_GOLDEN=1 uv run pytest tests/test_build_characterization.py

Two sources of non-determinism are neutralized so the manifests are stable across
machines and clones:

- `_now` (a catalog global, rendered as a date by `sitemap.xml.jx` and
  `metadata.jx`) is frozen, so a run crossing midnight cannot flake.
- Asset fingerprints are derived from file mtimes, which differ per checkout, so
  the `?v=...` query strings are normalized away before hashing.
"""

import hashlib
import importlib.util
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from writeadoc import Docs


PROJECT_ROOT = Path(__file__).parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs"
GOLDEN_DIR = Path(__file__).parent / "golden"

FROZEN_NOW = datetime(2024, 1, 1, tzinfo=timezone.utc)
RX_FINGERPRINT = re.compile(rb"\?v=[0-9a-f]+")
# Only text outputs carry rewritten asset URLs; binary assets are hashed as-is.
NORMALIZED_SUFFIXES = (".html", ".xml", ".txt")

UPDATE_GOLDEN = os.environ.get("WRITEADOC_UPDATE_GOLDEN") == "1"


# Helpers


def load_real_docs() -> Docs:
    """Import `docs/docs.py` fresh and return the `Docs` instance it configures."""
    sys.modules.pop("_docs_conf", None)
    spec = importlib.util.spec_from_file_location("_docs_conf", DOCS_ROOT / "docs.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["_docs_conf"] = module
    spec.loader.exec_module(module)
    return module.docs


def freeze_now(docs: Docs) -> None:
    """Pin the `_now` catalog global of a project and all its variants."""
    for instance in (docs, *docs.variants.values()):
        instance.catalog.jinja_env.globals["_now"] = FROZEN_NOW


def snapshot(build_dir: Path) -> str:
    """Render a build directory as a sorted `sha256  path` manifest."""
    lines = []
    for path in sorted(build_dir.rglob("*")):
        rel = path.relative_to(build_dir).as_posix()
        # `is_symlink` must be checked first: `is_file` follows symlinks.
        if path.is_symlink():
            lines.append(f"{'symlink':<64}  {rel}")
        elif path.is_file():
            data = path.read_bytes()
            if path.suffix in NORMALIZED_SUFFIXES:
                data = RX_FINGERPRINT.sub(b"?v=FINGERPRINT", data)
            lines.append(f"{hashlib.sha256(data).hexdigest()}  {rel}")
    return "\n".join(lines) + "\n"


def parse_manifest(manifest: str) -> dict[str, str]:
    entries = {}
    for line in manifest.splitlines():
        digest, _, rel = line.partition("  ")
        entries[rel.strip()] = digest.strip()
    return entries


def describe_diff(expected: str, actual: str) -> str:
    exp = parse_manifest(expected)
    act = parse_manifest(actual)
    added = sorted(set(act) - set(exp))
    removed = sorted(set(exp) - set(act))
    changed = sorted(rel for rel in set(exp) & set(act) if exp[rel] != act[rel])

    report = []
    for label, paths in (
        ("unexpected new files", added),
        ("missing files", removed),
        ("changed contents", changed),
    ):
        if paths:
            shown = ", ".join(paths[:10])
            extra = f" (+{len(paths) - 10} more)" if len(paths) > 10 else ""
            report.append(f"  {len(paths)} {label}: {shown}{extra}")
    return "\n".join(report)


def assert_matches_golden(name: str, build_dir: Path) -> None:
    actual = snapshot(build_dir)
    golden = GOLDEN_DIR / f"{name}.txt"

    if UPDATE_GOLDEN:
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        golden.write_text(actual, encoding="utf-8")
        pytest.skip(f"Golden manifest updated: {golden.relative_to(PROJECT_ROOT)}")

    if not golden.exists():
        pytest.fail(
            f"No golden manifest for '{name}'. Generate it with:\n"
            f"  WRITEADOC_UPDATE_GOLDEN=1 uv run pytest {Path(__file__).name}"
        )

    expected = golden.read_text(encoding="utf-8")
    assert actual == expected, (
        f"Build output for '{name}' changed:\n"
        f"{describe_diff(expected, actual)}\n\n"
        f"Inspect the actual output in: {build_dir}\n"
        f"If the change is intentional, regenerate with:\n"
        f"  WRITEADOC_UPDATE_GOLDEN=1 uv run pytest {Path(__file__).name}"
    )


# The real `docs/` project


def test_docs_devmode_build(tmp_path):
    """`build(devmode=True)`: symlinked assets, no fingerprinting."""
    docs = load_real_docs()
    freeze_now(docs)
    docs._set_build_target(build_dir=tmp_path, prefix=docs.build_target.prefix)

    docs.build(devmode=True, boring=True)

    assert_matches_golden("docs_devmode", tmp_path)


def test_docs_release_build(tmp_path):
    """`build(devmode=False, llm=True)`: copied assets, fingerprinted URLs, llms.txt."""
    docs = load_real_docs()
    freeze_now(docs)
    docs._set_build_target(build_dir=tmp_path, prefix=docs.build_target.prefix)

    docs.build(devmode=False, llm=True, boring=True)

    assert_matches_golden("docs_release", tmp_path)


# A synthetic project exercising prefixes and variants
#
# The real `docs/` project has no prefix and no variants, so `_add_prefix_to_urls`,
# the variant `build_dir`/`prefix` propagation in `cli_build`, and the prefixed
# branch of `_fingerprint_assets` are otherwise never exercised.


PAGE_VIEW = """
<link rel="stylesheet" href="/assets/style.css">
<h1>{{ page.title }}</h1>
{{ page.content }}
<a href="/docs/two/">two</a>
""".strip()

# Mirrors `docs/views/robots.txt.jx`: reads both `docs.prefix` and the variants,
# so the manifest captures how prefixes are propagated.
ROBOTS_VIEW = """
User-Agent: *
Disallow: {{ build.base_url }}search/
{% for variant in build.variants.values() -%}
Disallow: {{ variant.base_url }}search/
{% endfor -%}
Sitemap: {{ site.base_url }}/sitemap.xml
""".strip()

LLM_VIEW = """
{% for page in site.pages|selectattr("source")|list %}
{{ page.render_metadata(url=page.url)|safe }}

{{ page.source|safe }}
{% endfor %}
""".strip()


def write_variants_project(root: Path) -> Docs:
    (root / "content" / "es").mkdir(parents=True)
    (root / "views").mkdir()
    (root / "assets").mkdir()

    (root / "assets" / "style.css").write_text("body { color: red; }\n")

    (root / "views" / "page.jx").write_text(PAGE_VIEW)
    (root / "views" / "index.jx").write_text("<h1>{{ site.name }}</h1>")
    (root / "views" / "search.jx").write_text("<h1>Search</h1>")
    (root / "views" / "robots.txt.jx").write_text(ROBOTS_VIEW)
    (root / "views" / "llm.jx").write_text(LLM_VIEW)

    for lang, folder in (("en", root / "content"), ("es", root / "content" / "es")):
        (folder / "index.md").write_text(f"---\ntitle: Home {lang}\n---\n\nWelcome.")
        (folder / "one.md").write_text(
            f"---\ntitle: One {lang}\n---\n\nSee [two](/docs/two/) and ![css](/assets/style.css)."
        )
        (folder / "two.md").write_text(f"---\ntitle: Two {lang}\n---\n\nThe end.")

    variant = Docs(
        root,
        pages=["one.md", "two.md"],
        site={"name": "Docs ES", "lang": "es", "base_url": "https://example.test"},
    )
    return Docs(
        root,
        pages=["one.md", "two.md"],
        site={
            "name": "Docs",
            "lang": "en",
            "version": "2.5",
            "base_url": "https://example.test",
        },
        variants={"es": variant},
    )


def test_variants_archive_build(tmp_path):
    """`cli_build(archive=True)`: version prefix on the main site, nested on variants."""
    docs = write_variants_project(tmp_path)
    freeze_now(docs)

    docs.cli_build(archive=True, llm=True, boring=True)

    assert_matches_golden("variants_archive", tmp_path / "archive")


def test_variants_release_build(tmp_path):
    """`cli_build(archive=False)`: unprefixed main site, prefixed variant."""
    docs = write_variants_project(tmp_path)
    freeze_now(docs)

    docs.cli_build(archive=False, llm=True, boring=True)

    assert_matches_golden("variants_release", tmp_path / "build")
