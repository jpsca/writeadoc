from writeadoc.md import render_markdown


def test_inline_html():
    """The content inside should be processed as markdown."""
    source = (
        """The <span title="meh">_HTML_</span> specification\n"""
    )
    expected = """<p>The <span title="meh"><em>HTML</em></span> specification</p>\n"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected


def test_inline_tag():
    """The content inside should be processed as markdown."""
    source = (
        """The <Test title="meh">_HTML_</Test> specification\n"""
    )
    expected = """<p>The <Test title="meh"><em>HTML</em></Test> specification</p>\n"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected


def test_block_html():
    """The content inside should be treated as a raw block."""
    source = """lorem

<h2>Hello **World**</h2>

ipsum
"""
    expected = """<p>lorem</p>
<h2>Hello **World**</h2>

<p>ipsum</p>
"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected


def test_block_html_like():
    source = """lorem

<Test>Hello **World**</Test>

ipsum
"""
    expected = """<p>lorem</p>
<Test>Hello **World**</Test>

<p>ipsum</p>
"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected


def test_block_tag_with_attrs():
    source = """lorem

<Card class="hi">This **is** a test</Card>

ipsum
"""
    expected = """<p>lorem</p>
<Card class="hi">This **is** a test</Card>

<p>ipsum</p>
"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected


def test_block_html_like_group():
    source = """lorem

<Lorem>Hello World</Lorem>
<Ipsum>Hello World</Ipsum>

ipsum
"""
    expected = """<p>lorem</p>
<Lorem>Hello World</Lorem>
<Ipsum>Hello World</Ipsum>

<p>ipsum</p>
"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected


def test_block_html_like_nested():
    source = """lorem

<Card>
<Header>Hello World</Header>
</Card>

ipsum
"""
    expected = """<p>lorem</p>
<Card>
<Header>Hello World</Header>
</Card>

<p>ipsum</p>
"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected


def test_block_html_like_nested_with_spaces():
    source = """lorem

<Card>
  <Header>Hello World</Header>
</Card>

ipsum
"""
    expected = """<p>lorem</p>
<Card>
  <Header>Hello World</Header>
</Card>

<p>ipsum</p>
"""
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected
