# from writeadoc import Docs


# def test_render_components(tmp_root):
#     (tmp_root / "comp").mkdir()
#     (tmp_root / "comp" / "test.jinja").write_text("""
# <h2 {{ attrs.render() }}>{{ content }}</h2>
# """)

#     (tmp_root / "content" / "test.md").write_text("""
# ---
# title: Test Page
# imports:
#   "Test": "test.jinja"
# ---
# <Test>This **is** a test</Test>

# <Test class="hi">Hello world</Test>
# """.strip())

#     docs = Docs(tmp_root, pages=["test.md"])
#     docs.catalog.add_folder(tmp_root / "comp")
#     docs.build()

#     expected = """
# <h1>Test Page</h1>
# <h2 >This **is** a test</h2>

# <h2 class="hi">Hello world</h2>
# """.strip()
#     result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
#     print(result)
#     assert result == expected


# def test_render_markdown_inline(tmp_root):
#     (tmp_root / "comp").mkdir()
#     (tmp_root / "comp" / "test.jinja").write_text("<h2 {{ attrs.render() }}>{{ content }}</h2>")

#     (tmp_root / "content" / "test.md").write_text("""
# ---
# title: Test Page
# imports:
#   "Test": "test.jinja"
# ---
# <Test markdown="span" class="hi">This **is** a test</Test>
# """.strip())

#     docs = Docs(tmp_root, pages=["test.md"])
#     docs.catalog.add_folder(tmp_root / "comp")
#     docs.build()

#     expected = """
# <h1>Test Page</h1>
# <h2 class="hi">This <strong>is</strong> a test</h2>
# """.strip()
#     result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
#     print(result)
#     assert result == expected


# def test_render_markdown_block(tmp_root):
#     (tmp_root / "comp").mkdir()
#     (tmp_root / "comp" / "test.jinja").write_text("<h2 {{ attrs.render() }}>{{ content }}</h2>")

#     (tmp_root / "content" / "test.md").write_text("""
# ---
# title: Test Page
# imports:
#   "Test": "test.jinja"
# ---
# <Test markdown="1" class="hi">This **is** a test</Test>
# """.strip())

#     docs = Docs(tmp_root, pages=["test.md"])
#     docs.catalog.add_folder(tmp_root / "comp")
#     docs.build()

#     expected = """
# <h1>Test Page</h1>
# <h2 class="hi"><p>This <strong>is</strong> a test</p></h2>
# """.strip()
#     result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
#     print(result)
#     assert result == expected


# def test_self_closing_components(tmp_root):
#     (tmp_root / "comp").mkdir()
#     (tmp_root / "comp" / "test.jinja").write_text("<h2 {{ attrs.render() }}>Hello</h2>")

#     (tmp_root / "content" / "test.md").write_text("""
# ---
# title: Test Page
# imports:
#   "Test": "test.jinja"
# ---
# <Test class="hi" />
# """.strip())

#     docs = Docs(tmp_root, pages=["test.md"])
#     docs.catalog.add_folder(tmp_root / "comp")
#     docs.build()

#     expected = """
# <h1>Test Page</h1>
# <h2 class="hi">Hello</h2>
# """.strip()
#     result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
#     print(result)
#     assert result == expected


# def test_tags_inside_code(tmp_root):
#     (tmp_root / "comp").mkdir()
#     (tmp_root / "comp" / "test.jinja").write_text("<h2>{{ content }}</h2>")

#     (tmp_root / "content" / "test.md").write_text("""
# ---
# title: Test Page
# imports:
#   "Test": "test.jinja"
# ---
# <Test>This **is** a test</Test>

# ```
# <Test />
# <Test></Test>
# ```
# """.strip())

#     docs = Docs(tmp_root, pages=["test.md"])
#     docs.catalog.add_folder(tmp_root / "comp")
#     docs.build()

#     expected = """
# <h1>Test Page</h1>
# <h2>This **is** a test</h2>

# <div class="language-text highlight"><pre><code>&lt;Test /&gt;
# &lt;Test&gt;&lt;/Test&gt;
# </code></pre></div>
# """.strip()
#     result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
#     print(result)
#     assert result == expected


# def test_ignore_jinja_expr(tmp_root):
#     (tmp_root / "comp").mkdir()
#     (tmp_root / "comp" / "test.jinja").write_text("<h2>{{ content }}</h2>")

#     (tmp_root / "content" / "test.md").write_text("""
# ---
# title: Test Page
# imports:
#   "Test": "test.jinja"
# ---
# <Test>This **is** a test</Test>

# {{ this is not a variable }}

# {% if test %}Nor this {%- endif %}

# {# or this #}
# """.strip())

#     docs = Docs(tmp_root, pages=["test.md"])
#     docs.catalog.add_folder(tmp_root / "comp")
#     docs.build()

#     expected = """
# <h1>Test Page</h1>
# <h2>This **is** a test</h2>

# <p>{{ this is not a variable }}</p>
# <p>{% if test %}Nor this {%- endif %}</p>
# <p>{# or this #}</p>
# """.strip()
#     result = (tmp_root / "build" / "docs" / "test" / "index.html").read_text()
#     print(result)
#     assert result == expected
