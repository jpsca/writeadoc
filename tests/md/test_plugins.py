import pytest

from writeadoc.md import render_markdown


TEST_CASES = [
    (  # abbr
        """
The HTML specification
is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium
""",
        """<p>The <abbr title="Hyper Text Markup Language">HTML</abbr> specification
is maintained by the <abbr title="World Wide Web Consortium">W3C</abbr>.</p>
"""),

    (  # footnotes
        """
content in paragraph with footnote[^1] markup.

[^1]: footnote explain
""",
        """<p>content in paragraph with footnote<sup class="footnote-ref" id="fnref-1"><a href="#fn-1">1</a></sup> markup.</p>
<section class="footnotes">
<ol>
<li id="fn-1"><p>footnote explain<a href="#fnref-1" class="footnote">&#8617;</a></p></li>
</ol>
</section>
"""),

    (  # tables
        """
| Left Header  |  Center Header  | Right Header  |
| :----------- | :-------------: | ------------: |
| Content Cell |  Content Cell   | Content Cell  |
""",
        """<table>
<thead>
<tr>
  <th style="text-align:left">Left Header</th>
  <th style="text-align:center">Center Header</th>
  <th style="text-align:right">Right Header</th>
</tr>
</thead>
<tbody>
<tr>
  <td style="text-align:left">Content Cell</td>
  <td style="text-align:center">Content Cell</td>
  <td style="text-align:right">Content Cell</td>
</tr>
</tbody>
</table>
"""),

    (  # task lists
        """
- [x] item 1
- [ ] item 2
""",
        """<ul depth="0">
<li class="task-list-item"><input class="task-list-item-checkbox" type="checkbox" disabled checked/>item 1</li>
<li class="task-list-item"><input class="task-list-item-checkbox" type="checkbox" disabled/>item 2</li>
</ul>
"""),

    (  # def_list
        """
First term
: First definition
: Second definition

Second term
: Third definition
""",
        """<dl>
<dt>First term</dt>
<dd>First definition</dd>
<dd>Second definition</dd>
<dt>Second term</dt>
<dd>Third definition</dd>
</dl>
"""),

    (  # admonition
    """
::: note
This is a note admonition
:::
""",
    """<section class="admonition note">
<p class="admonition-title">Note</p>
<p>This is a note admonition</p>
</section>
"""),

    (  # admonition with title
    """
::: note Custom Title
This is a note admonition
:::
""",
    """<section class="admonition note">
<p class="admonition-title">Custom Title</p>
<p>This is a note admonition</p>
</section>
"""),

    (  # details
    """
::: note
:open: true

This is a note admonition
:::
""",
    """<details class="admonition note" open>
<summary class="admonition-title">Note</summary>
<p>This is a note admonition</p>
</details>
"""),

    (  # details with title
    """
::: note Custom Title
:open: true

This is a note admonition
:::
""",
    """<details class="admonition note" open>
<summary class="admonition-title">Custom Title</summary>
<p>This is a note admonition</p>
</details>
"""),

    (  # details closed
    """
::: note
:open: false

This is a note admonition
:::
""",
    """<details class="admonition note">
<summary class="admonition-title">Note</summary>
<p>This is a note admonition</p>
</details>
"""),

    (  # include markdown
    """
::: include test.md
:::
""",
    """<h1 id="hello-world">Hello world</h1>
"""),

    (  # include html
    """
::: include test.html
:::
""",
    """<p>Lorem Ipsum</p>
"""),

    (  # include error
    """
::: include nonexistent.md
:::
""",
    """<div class="error"><pre>Could not find file: nonexistent.md</pre></div>
"""),

    (  # container
    """
::: div grid

This is *inside* a container.
:::
""",
    """<div class="grid">
<p>This is <em>inside</em> a container.</p>
</div>
"""),
]


@pytest.mark.parametrize("source, expected", TEST_CASES)
def test_render_plugins(source, expected):
    result = render_markdown(source, __file__=__file__)[0]
    print(result)
    assert result == expected
