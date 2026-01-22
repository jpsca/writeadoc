import pytest

from .highlight import block_code


TEST_CASES = [
    (
        "",
        """
console.log("Hello world");
""",
        """<pre><code>console.log(&quot;Hello world&quot;);</code></pre>
""",
    ),
    (
        "javascript",
        """
console.log("Hello world");
""",
        """<div class="highlight lang-javascript"><pre><code><span class="nx">console</span><span class="p">.</span><span class="nx">log</span><span class="p">(</span><span class="s2">&quot;Hello world&quot;</span><span class="p">);</span>
</code></pre></div>
""",
    ),
    (
        'python {linenums="1"}',
        """
import foo.bar

a = "lorem"
b = "ipsum"
""",
        """<div class="highlight lang-python"><pre><code><span data-linenos="1"></span><span class="kn">import</span><span class="w"> </span><span class="nn">foo.bar</span>
<span data-linenos="2"></span>
<span data-linenos="3"></span><span class="n">a</span> <span class="o">=</span> <span class="s2">&quot;lorem&quot;</span>
<span data-linenos="4"></span><span class="n">b</span> <span class="o">=</span> <span class="s2">&quot;ipsum&quot;</span>
</code></pre></div>
"""
    ),
    (
        'python   linenums="1"   ',
        """
import foo.bar

a = "lorem"
b = "ipsum"
""",
        """<div class="highlight lang-python"><pre><code><span data-linenos="1"></span><span class="kn">import</span><span class="w"> </span><span class="nn">foo.bar</span>
<span data-linenos="2"></span>
<span data-linenos="3"></span><span class="n">a</span> <span class="o">=</span> <span class="s2">&quot;lorem&quot;</span>
<span data-linenos="4"></span><span class="n">b</span> <span class="o">=</span> <span class="s2">&quot;ipsum&quot;</span>
</code></pre></div>
"""
    ),
    (
        'python {linenums="42"}',
        """
import foo.bar

a = "lorem"
b = "ipsum"
""",
        """<div class="highlight lang-python"><pre><code><span data-linenos="42"></span><span class="kn">import</span><span class="w"> </span><span class="nn">foo.bar</span>
<span data-linenos="43"></span>
<span data-linenos="44"></span><span class="n">a</span> <span class="o">=</span> <span class="s2">&quot;lorem&quot;</span>
<span data-linenos="45"></span><span class="n">b</span> <span class="o">=</span> <span class="s2">&quot;ipsum&quot;</span>
</code></pre></div>
"""
    ),
    (
        'python {linenums="1 2"}',
        """
import foo.bar

a = "lorem"
b = "ipsum"
""",
        """<div class="highlight lang-python"><pre><code><span data-linenos=" "></span><span class="kn">import</span><span class="w"> </span><span class="nn">foo.bar</span>
<span data-linenos="2"></span>
<span data-linenos=" "></span><span class="n">a</span> <span class="o">=</span> <span class="s2">&quot;lorem&quot;</span>
<span data-linenos="4"></span><span class="n">b</span> <span class="o">=</span> <span class="s2">&quot;ipsum&quot;</span>
</code></pre></div>
"""
    ),
    (
        'python {hl_lines="1 3"}',
        '''
"""Some file."""
import foo.bar
import boo.baz
import foo.bar.baz
''',
        """<div class="highlight lang-python"><pre><code><span class="hll"><span class="sd">&quot;&quot;&quot;Some file.&quot;&quot;&quot;</span>
</span><span class="kn">import</span><span class="w"> </span><span class="nn">foo.bar</span>
<span class="hll"><span class="kn">import</span><span class="w"> </span><span class="nn">boo.baz</span>
</span><span class="kn">import</span><span class="w"> </span><span class="nn">foo.bar.baz</span>
</code></pre></div>
"""
    ),
    (
        'python {linenums="42" hl_lines="2"}',
        """
def foobar():
    a = "lorem"
    b = "ipsum"

foobar()
""",
        """<div class="highlight lang-python"><pre><code><span data-linenos="42"></span><span class="k">def</span><span class="w"> </span><span class="nf">foobar</span><span class="p">():</span>
<span class="hll"><span data-linenos="43"></span>    <span class="n">a</span> <span class="o">=</span> <span class="s2">&quot;lorem&quot;</span>
</span><span data-linenos="44"></span>    <span class="n">b</span> <span class="o">=</span> <span class="s2">&quot;ipsum&quot;</span>
<span data-linenos="45"></span>
<span data-linenos="46"></span><span class="n">foobar</span><span class="p">()</span>
</code></pre></div>
"""
    ),
    (
        'python {title="cool_file.py"}',
        """
import foo
""",
        """<div class="highlight lang-python"><span class="filename">cool_file.py</span><pre><code><span class="kn">import</span><span class="w"> </span><span class="nn">foo</span>
</code></pre></div>
"""
    ),
]


@pytest.mark.parametrize("info, code, expected", TEST_CASES)
def test_block_code(info, code, expected):
    result = block_code(code, info)
    print(result)
    assert result == expected
