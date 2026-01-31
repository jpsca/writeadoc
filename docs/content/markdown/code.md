---
title: Code blocks
icon: icons/code.svg
---

To include a code block in your document, place three backticks (` ``` `) before and after the code block and, optionally, add a language name.
Leave one blank line before and after the block for easier reading.

::: div example
````md
```javascript
console.log("Hello world");
```
````

```javascript
console.log("Hello world");
```
:::

::: tip |  Tip: Display triple backticks in a code block
You can always add _more_ backticks! For example, to display triple backticks in a code block, wrap them inside quadruple backticks.

`````md
````md
```
Look! You can see my backticks.
```
````
`````

renders as:

````md
```
Look! You can see my backticks.
```
````
:::


## Syntax highlighting

To make your code block clearer, specify the language right after the first three backticks to enable syntax highlighting.

::: div example
````md
```python
print("Hello, world!")
for i in range(10):
    print(i)
```
````

renders as:

```python
print("Hello, world!")
for i in range(10):
    print(i)
```
:::

Internally, this uses the **Pygments** library. Check the [long list of available languages](https://pygments.org/languages/).
This only adds HTML classes; the styles and colors themselves are controlled by CSS.


## Showing Line Numbers

To show line numbers in your code block, specify the starting line number with the option `linenums="1"` after the opening tokens (and language, if present).
The number _must_ be quoted, and it is the number of the first line (it must be greater than 0).

::: div example
````md
```python {linenums="1"}
import foo.bar

a = "lorem"
b = "ipsum"
```
````

renders as:

```python {linenums="1"}
import foo.bar

a = "lorem"
b = "ipsum"
```
:::

If you want to start with a different line number, simply specify a number other than `1`.

::: div example
````md
```python {linenums="42"}
def foobar():
    a = "lorem"
    b = "ipsum"

foobar()
```
````

renders as:

```python {linenums="42"}
def foobar():
    a = "lorem"
    b = "ipsum"

foobar()
```
:::

Pygments also has a few additional options regarding line numbers. One is "line step," which, if set to a number larger than 1, will print only every n^th^ line number.

::: div example
````md
```python {linenums="1 2"}
"""Some file."""
import foo.bar
import boo.baz
import foo.bar.baz
```
````

renders as:

```python {linenums="1 2"}
"""Some file."""
import foo.bar
import boo.baz
import foo.bar.baz
```
:::


## Highlighting lines

You can specify certain lines for highlighting by using the `hl_lines` setting directly after the opening tokens (and language, if present), with the targeted line numbers separated by spaces.

::: div example
````md
```python {hl_lines="1 3"}
"""Some file."""
import foo.bar
import boo.baz
import foo.bar.baz
```
````

renders as:

```python {hl_lines="1 3"}
"""Some file."""
import foo.bar
import boo.baz
import foo.bar.baz
```
:::

Line numbers are always referenced starting at 1, regardless of what the line number is labeled as when showing line numbers.

::: div example
````md
```python {linenums="42" hl_lines="2"}
def foobar():
    a = "lorem"
    b = "ipsum"

foobar()
```
````

renders as:

```python {linenums="42" hl_lines="2"}
def foobar():
    a = "lorem"
    b = "ipsum"

foobar()
```
:::

If you'd like to highlight a range of lines, you can use the notation x-y, where x is the starting line and y is the ending line. You can specify multiple ranges and even mix them with individual lines.

::: div example
````md
```python {hl_lines="1-2 5 7-8"}
import foo
import boo.baz
import foo.bar.baz

class Foo:
   def __init__(self):
       self.foo = None
       self.bar = None
       self.baz = None
```
````

renders as:

```python {hl_lines="1-2 5 7-8"}
import foo
import boo.baz
import foo.bar.baz

class Foo:
   def __init__(self):
       self.foo = None
       self.bar = None
       self.baz = None
```
:::


## Title Headers

A header with a title can be applied to a code block using the title option. Typically, you use it to show a filename, but it can be anything.

::: div example
````md
```python {title="cool_file.py"}
import foo
import boo.baz
import foo.bar.baz

class Foo:
   def __init__(self):
       self.foo = None
       self.bar = None
       self.baz = None
```
````

renders as:

```python {title="cool_file.py"}
import foo
import boo.baz
import foo.bar.baz

class Foo:
   def __init__(self):
       self.foo = None
       self.bar = None
       self.baz = None
```
:::
