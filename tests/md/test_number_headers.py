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
        '<h2 id="a-section">1. A section</h2>\n'
        '<h3 id="lorem">1.1 lorem</h3>\n'
        '<h3 id="ipsum">1.2 ipsum</h3>\n'
        '<h2 id="another-section">2. Another section</h2>\n'
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
