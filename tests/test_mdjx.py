from writeadoc import Docs


def test_render_components(tmp_root):
    (tmp_root / "comp").mkdir()
    (tmp_root / "comp" / "test.jinja").write_text("""
<h2 {{ attrs.render() }}>{{ content }}</h2>
""")

    (tmp_root / "content" / "test.md").write_text("""
---
title: Test Page
imports:
  "Test": "test.jinja"
---
<Test>This **is** a test</Test>

<Test class="hi">Hello world</Test>
""".strip())

    docs = Docs(tmp_root, pages=["test.md"])
    docs.catalog.add_folder(tmp_root / "comp")
    docs.build()

    expected = """
<h1>Test Page</h1>
<h2 >This **is** a test</h2>
<h2 class="hi">Hello world</h2>
""".strip()
    result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
    print(result)
    assert result == expected


def test_render_markdown_inline(tmp_root):
    (tmp_root / "comp").mkdir()
    (tmp_root / "comp" / "test.jinja").write_text("<span {{ attrs.render() }}>{{ content }}</span>")

    (tmp_root / "content" / "test.md").write_text("""
---
title: Test Page
imports:
  "Test": "test.jinja"
---
Lorem <Test class="hi">This **is** a test</Test> Ipsum
""".strip())

    docs = Docs(tmp_root, pages=["test.md"])
    docs.catalog.add_folder(tmp_root / "comp")
    docs.build()

    expected = """
<h1>Test Page</h1>
<p>Lorem <span class="hi">This <strong>is</strong> a test</span> Ipsum</p>
""".strip()
    result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
    print(result)
    assert result == expected


def test_self_closing_components(tmp_root):
    (tmp_root / "comp").mkdir()
    (tmp_root / "comp" / "test.jinja").write_text("<h2 {{ attrs.render() }}>Hello</h2>")

    (tmp_root / "content" / "test.md").write_text("""
---
title: Test Page
imports:
  "Test": "test.jinja"
---

<Test class="hi" />
""".strip())

    docs = Docs(tmp_root, pages=["test.md"])
    docs.catalog.add_folder(tmp_root / "comp")
    docs.build()

    expected = """
<h1>Test Page</h1>
<h2 class="hi">Hello</h2>
""".strip()
    result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
    print(result)
    assert result == expected


def test_tags_inside_code(tmp_root):
    (tmp_root / "comp").mkdir()
    (tmp_root / "comp" / "test.jinja").write_text("<h2>{{ content }}</h2>")

    (tmp_root / "content" / "test.md").write_text("""
---
title: Test Page
imports:
  "Test": "test.jinja"
---
<Test>This **is** a test</Test>

```
<Test />
<Test></Test>
```
""".strip())

    docs = Docs(tmp_root, pages=["test.md"])
    docs.catalog.add_folder(tmp_root / "comp")
    docs.build()

    expected = """
<h1>Test Page</h1>
<h2>This **is** a test</h2>
<pre><code>&lt;Test /&gt;
&lt;Test&gt;&lt;/Test&gt;</code></pre>
""".strip()
    result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
    print(result)
    assert result == expected


def test_gt_in_attribute_value(tmp_root):
    """Test that > characters inside quoted attribute values are handled correctly."""
    (tmp_root / "comp").mkdir()
    (tmp_root / "comp" / "test.jinja").write_text("<div {{ attrs.render() }}>{{ content }}</div>")

    (tmp_root / "content" / "test.md").write_text("""
---
title: Test Page
imports:
  "Test": "test.jinja"
---
<Test data-expr="a > b">Content</Test>

<Test data-expr='x > y' />
""".strip())

    docs = Docs(tmp_root, pages=["test.md"])
    docs.catalog.add_folder(tmp_root / "comp")
    docs.build()

    expected = """
<h1>Test Page</h1>
<div data-expr="a > b">Content</div>
<div data-expr="x > y"></div>
""".strip()
    result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
    print(result)
    assert result == expected


def test_ignore_jinja_expr(tmp_root):
    (tmp_root / "comp").mkdir()
    (tmp_root / "comp" / "test.jinja").write_text("<h2>{{ content }}</h2>")

    (tmp_root / "content" / "test.md").write_text("""
---
title: Test Page
imports:
  "Test": "test.jinja"
---
<Test>This **is** a test</Test>

\{\{ this is not a variable }}

\{% if test %}Nor this \{%- endif %}

\{# or this #}
""".strip())

    docs = Docs(tmp_root, pages=["test.md"])
    docs.catalog.add_folder(tmp_root / "comp")
    docs.build()

    expected = """
<h1>Test Page</h1>
<h2>This **is** a test</h2>
<p>{{ this is not a variable }}</p>
<p>{% if test %}Nor this {%- endif %}</p>
<p>{# or this #}</p>
""".strip()
    result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
    print(result)
    assert result == expected
