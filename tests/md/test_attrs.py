import pytest

from writeadoc.md import render_markdown


TEST_CASES = [
    (  # Classes shortcut
        """![Nav A](/assets/images/nav-page-light.png){ .only-light .right }""",
        """<p><img alt="Nav A" class="only-light right" src="/assets/images/nav-page-light.png" /></p>
"""
    ),

    (  # Classes shortcut + attribute
        """![Nav A](/assets/images/nav-page-light.png){ .right class="only-light" }""",
        # first the attr, then the shortcut(s)
        """<p><img alt="Nav A" class="only-light right" src="/assets/images/nav-page-light.png" /></p>
"""
    ),

    (  # ID shortcut
        """[Meh](#meh){ #green }""",
        """<p><a href="#meh" id="green">Meh</a></p>
"""
    ),

    (  # ID shortcut + attr
        """[Meh](#meh){ #green id="red" }""",
        # last one defined wins
        """<p><a href="#meh" id="red">Meh</a></p>
"""
    ),

    (  # emphasis
        """a *b*{ .bla } c""",
        """<p>a <em class="bla">b</em> c</p>
"""
    ),

    (  # strong
        """a **b**{ .bla } c""",
        """<p>a <strong class="bla">b</strong> c</p>
"""
    ),

    (  # codespan
        """a `b`{ .bla } c""",
        """<p>a <code class="bla">b</code> c</p>
"""
    ),

    (  # paragraph
        """
lorem ipsum
{ .fancy }
""",
        """<p class="fancy">lorem ipsum</p>
"""
    ),

    (  # heading
        """
# Heading 1
{ .fancy }

# Heading 2
{ .fancy }

# Heading 3
{ .fancy }
""",
        """<h1 class="fancy" id="heading-1">Heading 1</h1>
<h1 class="fancy" id="heading-2">Heading 2</h1>
<h1 class="fancy" id="heading-3">Heading 3</h1>
"""
    ),

    (  # heading with custom id
        """
## Hello
{ #world }
""",
        """<h2 id="world">Hello</h2>
"""
    ),

    (  # thematic_break
        """
----
{ .fancy }
""",
        """<hr class="fancy"/>
"""
    ),

    (  # block_quote (ignore attrs)
        """
> This is the first line of the quote.
> This is the second line of the quote.
{ .fancy }
""",
        """<blockquote><p>This is the first line of the quote.
This is the second line of the quote.
</p>
</blockquote>
"""
    ),

    (  # ul list (ignore attrs)
        """
* One
* Two
* Three
{ .fancy }
""",
        """<ul depth="0">
<li>One</li>
<li>Two</li>
<li>Three
</li>
</ul>
"""
    ),

    (  # ol list (ignore attrs)
        """
1. One
2. Two
3. Three
{ .fancy }
""",
        """<ol depth="0">
<li>One</li>
<li>Two</li>
<li>Three
</li>
</ol>
"""
    ),

    (  # list_item (ignore attrs)
        """
* One
* Two{ .fancy }
* Three
""",
        """<ul depth="0">
<li>One</li>
<li>Two</li>
<li>Three</li>
</ul>
"""
    ),

    (  # strikethrough
        """~~here is the content~~{ .bla }""",
        """<p><del class="bla">here is the content</del></p>
"""
    ),

    ( # insert
        r"""^^insert me^^ ^^insert\^\^me^^{ .bla }""",
        """<p><ins>insert me</ins> <ins class="bla">insert^^me</ins></p>
"""
    ),

    ( # mark
        r"""==mark me== ==mark with\=\=equal=={ .bla }""",
        """<p><mark>mark me</mark> <mark class="bla">mark with==equal</mark></p>
"""
    ),

    ( # subscript
        """Hello~subscript~{ .bla }""",
        """<p>Hello<sub class="bla">subscript</sub></p>
"""
    ),

    ( # superscript
        """Hello^superscript^{ .bla }""",
        """<p>Hello<sup class="bla">superscript</sup></p>
"""
    ),
]


@pytest.mark.parametrize("source, expected", TEST_CASES)
def test_render_attrs(source, expected):
    result = render_markdown(source)[0]
    print(result)
    assert result == expected
