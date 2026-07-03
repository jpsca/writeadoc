from writeadoc.utils import extract_metadata


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
