"""Test for the AutodocExtension with configurable render function."""
import markdown

from writeadoc.extensions.autodoc import AutodocExtension


def renderer(name, level=None):
    if level is None:
        return f"# Documentation for {name}"
    return f"# Documentation for {name}, {level}"


def test_autodoc_block():
    """Test that the extension correctly processes autodoc blocks."""
    md = markdown.Markdown(extensions=[AutodocExtension(renderer=renderer)])
    test_md = "Hello world\n\n::: sample.module.Class\n\nBye"
    html = md.convert(test_md).strip()

    print(html)
    assert html == "<p>Hello world</p>\n<h1>Documentation for sample.module.Class</h1>\n<p>Bye</p>"

def test_autodoc_block_with_level():
    """Test that the extension correctly processes autodoc blocks with levels."""
    md = markdown.Markdown(extensions=[AutodocExtension(renderer=renderer)])
    test_md = "Hello world\n\n::: sample.module.Class 4\n\nBye"
    html = md.convert(test_md).strip()

    print(html)
    assert html == "<p>Hello world</p>\n<h1>Documentation for sample.module.Class, 4</h1>\n<p>Bye</p>"
