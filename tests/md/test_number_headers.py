from writeadoc.md import render_markdown


SOURCE = """\
# My title

## A section

### lorem

### ipsum

## Another section
"""


def test_number_headers_renders_numbered_headings():
    html, state = render_markdown(SOURCE, meta={"number_headers": True})

    assert html == (
        '<h1 id="my-title">My title</h1>\n'
        '<h2 id="a-section"><span class="num">1.</span> A section</h2>\n'
        '<h3 id="lorem"><span class="num">1.1</span> lorem</h3>\n'
        '<h3 id="ipsum"><span class="num">1.2</span> ipsum</h3>\n'
        '<h2 id="another-section"><span class="num">2.</span> Another section</h2>\n'
    )
    assert state["toc_items"] == [
        (1, "my-title", "My title"),
        (2, "a-section", "1. A section"),
        (3, "lorem", "1.1 lorem"),
        (3, "ipsum", "1.2 ipsum"),
        (2, "another-section", "2. Another section"),
    ]


def test_number_headers_counter_resets_between_pages():
    """The shared `md` instance must not leak counters across render calls."""
    render_markdown(SOURCE, meta={"number_headers": True})
    _, state = render_markdown(SOURCE, meta={"number_headers": True})

    assert state["toc_items"] == [
        (1, "my-title", "My title"),
        (2, "a-section", "1. A section"),
        (3, "lorem", "1.1 lorem"),
        (3, "ipsum", "1.2 ipsum"),
        (2, "another-section", "2. Another section"),
    ]
