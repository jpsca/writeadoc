from unittest.mock import call

import pytest

from writeadoc.main import Docs
from writeadoc.utils import RANDOM_MESSAGES


@pytest.fixture
def docs(tmp_root):
    (tmp_root / "comp").mkdir()
    (tmp_root / "comp" / "test.jx").write_text("<h2>{{ content }}</h2>")

    (tmp_root / "content" / "test.md").write_text(
        """
---
title: Test Page
imports:
  "Test": "test.jx"
---
<Test>This **is** a test</Test>

```
<Test />
<Test></Test>
```
""".strip()
    )

    docs = Docs(tmp_root, pages=["test.md"])
    docs.catalog.add_folder(tmp_root / "comp")
    return docs


def test_build_with_random_messages(mocker, docs):
    mocker.patch(
        "writeadoc.main.get_random_messages", return_value=["one", "two", "three"]
    )
    mock_print = mocker.patch("builtins.print")
    docs.build()
    assert mock_print.call_count == 5
    mock_print.assert_has_calls([
        call("one..."),
        call("Processing pages..."),
        call("two..."),
        call("Rendering pages..."),
        call("three..."),
    ])


def test_build_with_no_random_messages(mocker, docs):
    mocker.patch(
        "writeadoc.main.get_random_messages", return_value=["one", "two", "three"]
    )
    mock_print = mocker.patch("builtins.print")
    docs.build(boring=True)
    assert mock_print.call_count == 2
    mock_print.assert_has_calls([
        call("Processing pages..."),
        call("Rendering pages..."),
    ])


def test_archive_build_fingerprints_prefixed_assets(tmp_root):
    (tmp_root / "assets" / "app.css").write_text("body {}")
    (tmp_root / "views" / "page.jx").write_text(
        '<link href="/assets/app.css" rel="stylesheet">{{ page.content or content }}'
    )
    (tmp_root / "content" / "test.md").write_text("""
---
title: Test Page
---
Hello
""".strip())

    docs = Docs(tmp_root, pages=["test.md"], site={"version": "1.0"})
    docs.cli_build(archive=True, boring=True)

    result = (tmp_root / "archive" / "1.0" / "docs" / "test" / "index.html").read_text()
    assert 'href="/1.0/assets/app.css?v=' in result


@pytest.fixture
def docs_with_variant(tmp_root):
    (tmp_root / "content" / "es").mkdir()
    (tmp_root / "content" / "one.md").write_text("---\ntitle: One\n---\n\nHi.")
    (tmp_root / "content" / "es" / "one.md").write_text("---\ntitle: Uno\n---\n\nHola.")

    variant = Docs(tmp_root, pages=["one.md"], site={"lang": "es"})
    return Docs(tmp_root, pages=["one.md"], variants={"es": variant})


def _random_messages_in(output: str) -> list[str]:
    return [message for message in RANDOM_MESSAGES if f"{message}..." in output]


def test_boring_silences_the_variants_too(docs_with_variant, capsys):
    docs_with_variant.build(boring=True)

    assert _random_messages_in(capsys.readouterr().out) == []


def test_variants_are_not_silenced_without_boring(docs_with_variant, capsys):
    """Guards the test above: the messages do get printed when not boring."""
    docs_with_variant.build(boring=False)

    assert _random_messages_in(capsys.readouterr().out)
