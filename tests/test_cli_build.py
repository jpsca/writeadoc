from unittest.mock import call

import pytest

from writeadoc.main import Docs


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
