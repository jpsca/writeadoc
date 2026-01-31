import pytest

from writeadoc.md import render_markdown


TEST_CASES = [
    (  # basic two tabs
        """
::: tab | Label 1
Content 1
:::

::: tab | Label 2
Content 2
:::
""",
        """<div class="tabbed-set">
<input id="__tabbed_1_1" name="__tabbed_1" type="radio" checked>
<input id="__tabbed_1_2" name="__tabbed_1" type="radio">
<div class="tabbed-labels">
<label for="__tabbed_1_1">Label 1</label>
<label for="__tabbed_1_2">Label 2</label>
</div>
<div class="tabbed-panels">
<div class="tabbed-panel">
<p>Content 1</p>
</div>
<div class="tabbed-panel">
<p>Content 2</p>
</div>
</div>
</div>
"""),

    (  # markdown in labels
        """
::: tab | **Bold** Label
Content A
:::

::: tab | _Italic_ Label
Content B
:::
""",
        """<div class="tabbed-set">
<input id="__tabbed_1_1" name="__tabbed_1" type="radio" checked>
<input id="__tabbed_1_2" name="__tabbed_1" type="radio">
<div class="tabbed-labels">
<label for="__tabbed_1_1"><strong>Bold</strong> Label</label>
<label for="__tabbed_1_2"><em>Italic</em> Label</label>
</div>
<div class="tabbed-panels">
<div class="tabbed-panel">
<p>Content A</p>
</div>
<div class="tabbed-panel">
<p>Content B</p>
</div>
</div>
</div>
"""),

    (  # markdown in content
        """
::: tab | Tab 1
**Bold** and _italic_ content

- List item 1
- List item 2
:::

::: tab | Tab 2
> A blockquote
:::
""",
        """<div class="tabbed-set">
<input id="__tabbed_1_1" name="__tabbed_1" type="radio" checked>
<input id="__tabbed_1_2" name="__tabbed_1" type="radio">
<div class="tabbed-labels">
<label for="__tabbed_1_1">Tab 1</label>
<label for="__tabbed_1_2">Tab 2</label>
</div>
<div class="tabbed-panels">
<div class="tabbed-panel">
<p><strong>Bold</strong> and <em>italic</em> content</p>
<ul depth="1">
<li>List item 1</li>
<li>List item 2</li>
</ul>
</div>
<div class="tabbed-panel">
<blockquote><p>A blockquote</p>
</blockquote>
</div>
</div>
</div>
"""),

    (  # tabs with surrounding content
        """
Before tabs

::: tab | Tab A
Inside A
:::

::: tab | Tab B
Inside B
:::

After tabs
""",
        """<p>Before tabs</p>
<div class="tabbed-set">
<input id="__tabbed_1_1" name="__tabbed_1" type="radio" checked>
<input id="__tabbed_1_2" name="__tabbed_1" type="radio">
<div class="tabbed-labels">
<label for="__tabbed_1_1">Tab A</label>
<label for="__tabbed_1_2">Tab B</label>
</div>
<div class="tabbed-panels">
<div class="tabbed-panel">
<p>Inside A</p>
</div>
<div class="tabbed-panel">
<p>Inside B</p>
</div>
</div>
</div>
<p>After tabs</p>
"""),

    (  # single tab
        """
::: tab | Solo Tab
Solo content
:::
""",
        """<div class="tabbed-set">
<input id="__tabbed_1_1" name="__tabbed_1" type="radio" checked>
<div class="tabbed-labels">
<label for="__tabbed_1_1">Solo Tab</label>
</div>
<div class="tabbed-panels">
<div class="tabbed-panel">
<p>Solo content</p>
</div>
</div>
</div>
"""),

    (  # empty label
        """
::: tab |
No label content
:::

::: tab | Has Label
With label
:::
""",
        """<div class="tabbed-set">
<input id="__tabbed_1_1" name="__tabbed_1" type="radio" checked>
<input id="__tabbed_1_2" name="__tabbed_1" type="radio">
<div class="tabbed-labels">
<label for="__tabbed_1_1">1</label>
<label for="__tabbed_1_2">Has Label</label>
</div>
<div class="tabbed-panels">
<div class="tabbed-panel">
<p>No label content</p>
</div>
<div class="tabbed-panel">
<p>With label</p>
</div>
</div>
</div>
"""),
]


@pytest.mark.parametrize("source, expected", TEST_CASES)
def test_render_tabs(source, expected):
    result = render_markdown(source)[0]
    print(result)
    assert result == expected


def test_multiple_tab_sets():
    """Test that multiple tab sets get unique IDs."""
    source = """
::: tab | Set1 Tab1
Content 1
:::

::: tab | Set1 Tab2
Content 2
:::

Some text between sets

::: tab | Set2 Tab1
Content A
:::

::: tab | Set2 Tab2
Content B
:::
"""
    result, env = render_markdown(source)

    # Check that we have two tab sets
    assert env.get("_tab_set_counter") == 2

    # Check IDs are unique
    assert "__tabbed_1_1" in result
    assert "__tabbed_1_2" in result
    assert "__tabbed_2_1" in result
    assert "__tabbed_2_2" in result

    # Check names are correct for grouping
    assert 'name="__tabbed_1"' in result
    assert 'name="__tabbed_2"' in result


def test_new_option_forces_new_group():
    """Test that :new: true forces a tab to start a new group."""
    source = """
::: tab | Tab A
Content A
:::

::: tab | Tab B
Content B
:::

::: tab | Tab C
:new: true

New group content
:::

::: tab | Tab D
Also in new group
:::
"""
    result, env = render_markdown(source)

    # Check that we have two tab sets
    assert env.get("_tab_set_counter") == 2

    # First group has Tab A and Tab B
    assert "__tabbed_1_1" in result
    assert "__tabbed_1_2" in result

    # Second group has Tab C and Tab D
    assert "__tabbed_2_1" in result
    assert "__tabbed_2_2" in result

    # Verify the labels are in the right groups
    assert 'name="__tabbed_1"' in result
    assert 'name="__tabbed_2"' in result


def test_select_option():
    """Test that :select: true makes a tab selected by default."""
    source = """
::: tab | Tab 1
Content 1
:::

::: tab | Tab 2
:select: true

Selected by default
:::

::: tab | Tab 3
Content 3
:::
"""
    result, _ = render_markdown(source)

    # Tab 2 should be checked, not Tab 1
    assert 'id="__tabbed_1_1" name="__tabbed_1" type="radio">' in result  # no checked
    assert 'id="__tabbed_1_2" name="__tabbed_1" type="radio" checked>' in result
    assert 'id="__tabbed_1_3" name="__tabbed_1" type="radio">' in result  # no checked
