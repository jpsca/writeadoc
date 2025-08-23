"""Test for the AutodocExtension with configurable render function."""
import markdown

from writeadoc.extensions.autodoc import AutodocExtension


def renderer(name, level=None):
    return f"# Documentation for {name}, {level}"


def test_autodoc_block():
    """Test that the extension correctly processes autodoc blocks."""
    md = markdown.Markdown(extensions=[AutodocExtension(renderer=renderer)])
    test_md = "::: sample.module.Class"
    html = md.convert(test_md)

    assert "Documentation for sample.module.Class" in html

def test_autodoc_block_with_level():
    """Test that the extension correctly processes autodoc blocks with levels."""
    md = markdown.Markdown(extensions=[AutodocExtension(renderer=renderer)])
    test_md = "::: sample.module.Class 4"
    html = md.convert(test_md)

    assert "Documentation for sample.module.Class, 4" in html
