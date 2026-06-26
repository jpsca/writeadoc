from writeadoc import PageData
from writeadoc.search import extract_search_data


def test_extractor():
    html = """
<h1 id="introduction">Introduction</h1>
<p class="description">Jx is a Python library for creating reusable "components" - encapsulated template snippets that can take arguments and render to HTML. They are similar to React or Vue components, but they render on the server side, not in the&nbsp;browser.</p>
<p>Unlike Jinja's <code>{% include "..." %}</code> or macros, Jx components integrate naturally with the rest of your template code.</p>
<div class="language-html+jinja highlight"><pre><code><span class="linenos" data-linenos="1 "></span><span class="p">&lt;</span><span class="nt">div</span><span class="p">&gt;</span>
<span class="linenos" data-linenos="2 "></span>  <span class="p">&lt;</span><span class="nt">Card</span> <span class="na">class</span><span class="o">=</span><span class="s">"bg-gray"</span><span class="p">&gt;</span>
<span class="linenos" data-linenos="3 "></span>    <span class="p">&lt;</span><span class="nt">h1</span><span class="p">&gt;</span>Products<span class="p">&lt;/</span><span class="nt">h1</span><span class="p">&gt;</span>
<span class="linenos" data-linenos="4 "></span>    <span class="cp">{%</span> <span class="k">for</span> <span class="nv">product</span> <span class="k">in</span> <span class="nv">products</span> <span class="cp">%}</span>
<span class="linenos" data-linenos="5 "></span>      <span class="p">&lt;</span><span class="nt">Product</span> <span class="na">product</span><span class="o">=</span><span class="cp">{{</span> <span class="nv">product</span> <span class="cp">}}</span> <span class="s">/</span><span class="p">&gt;</span>
<span class="linenos" data-linenos="6 "></span>    <span class="cp">{%</span> <span class="k">endfor</span> <span class="cp">%}</span>
<span class="linenos" data-linenos="7 "></span>  <span class="p">&lt;/</span><span class="nt">Card</span><span class="p">&gt;</span>
<span class="linenos" data-linenos="8 "></span><span class="p">&lt;/</span><span class="nt">div</span><span class="p">&gt;</span>
</code></pre></div>
<h2 id="s-features">Features&nbsp;<a class="headerlink" href="#s-features"></a></h2>
<h3 id="s-simple">Simple&nbsp;<a class="headerlink" href="#s-simple"></a></h3>
<p>Jx components are simple Jinja templates. You use them as if they were HTML tags after importing them: they're easy to use and easy to read.</p>
<h3 id="s-encapsulated">Encapsulated&nbsp;<a class="headerlink" href="#s-encapsulated"></a></h3>
<p>They are independent of each other and can link to their own CSS and JS, so you can freely copy and paste components between applications.</p>
"""
    page = PageData(
        content=html,
        url="/docs/foobar/test-page/",
        section_title="Test Section",
        section_url="/docs/test-section/",
        meta = {
            "id": "page",
            "title": "Test Page",
        }
    )
    result = extract_search_data(page)
    print(result)
    assert result == {
        "/docs/foobar/test-page/#introduction1": {
            "title": "Introduction",
            "content": 'Jx is a Python library for creating reusable "components" - encapsulated template snippets that can take arguments and render to HTML. They are similar to React or Vue components, but they render on the server side, not in the browser.',
            "section": "Test Section",
            "url": "/docs/foobar/test-page/#introduction",
        },
        "/docs/foobar/test-page/#introduction2": {
            "title": "Introduction",
            "content": 'Unlike Jinja\'s {% include "..." %} or macros, Jx components integrate naturally with the rest of your template code.',
            "section": "Test Section",
            "url": "/docs/foobar/test-page/#introduction",
        },
        "/docs/foobar/test-page/#introduction3": {
            "title": "Introduction",
            "content": '<pre>&lt;div&gt;\n  &lt;Card class="bg-gray"&gt;\n    &lt;h1&gt;Products&lt;/h1&gt;\n    {% for product in products %}\n      &lt;Product product={{ product }} /&gt;\n    {% endfor %}\n  &lt;/Card&gt;\n&lt;/div&gt;\n</pre>',
            "section": "Test Section",
            "url": "/docs/foobar/test-page/#introduction",
        },
        "/docs/foobar/test-page/#s-simple4": {
            "title": "Simple",
            "content": "Jx components are simple Jinja templates. You use them as if they were HTML tags after importing them: they're easy to use and easy to read.",
            "section": "Test Section",
            "url": "/docs/foobar/test-page/#s-simple",
        },
        "/docs/foobar/test-page/#s-encapsulated5": {
            "title": "Encapsulated",
            "content": "They are independent of each other and can link to their own CSS and JS, so you can freely copy and paste components between applications.",
            "section": "Test Section",
            "url": "/docs/foobar/test-page/#s-encapsulated",
        },
    }


def test_extractor_nested_tags():
    """Deeply nested unwrap-tags (as produced by autodoc + Pygments) must not
    corrupt `<pre>` blocks, and removed tags must drop their contents.
    """
    html = """
<h2 id="api">API</h2>
<div class="autodoc"><div class="member"><div class="signature">
<pre><span class="kn">import</span> <span class="nn">peewee</span>
<span class="k">class</span> <span class="nc">Post</span><span class="p">(</span><span class="n">BaseModel</span><span class="p">):</span>
    <span class="n">title</span> <span class="o">=</span> <span class="n">pw</span><span class="o">.</span><span class="n">CharField</span><span class="p">()</span></pre>
</div></div></div>
<svg viewBox="0 0 10 10"><path d="M0 0"/></svg>
<script>console.log("drop me");</script>
<p>Trailing <a href="#x"><code>text</code></a> kept.</p>
"""
    page = PageData(
        content=html,
        url="/docs/api/",
        section_title="API",
        meta={"id": "api", "title": "API"},
    )
    result = extract_search_data(page)

    # The code block survives intact (the old paired-regex split it apart).
    pre_frag = result["/docs/api/#api1"]["content"]
    assert pre_frag.startswith("<pre>import peewee")
    assert "class Post(BaseModel):" in pre_frag
    assert "title = pw.CharField()" in pre_frag
    assert pre_frag.endswith("</pre>")

    # Stripped-with-contents tags leave no trace; unwrapped tags keep their text.
    joined = " ".join(frag["content"] for frag in result.values())
    assert "drop me" not in joined
    assert "viewBox" not in joined
    assert "Trailing text kept." in joined
