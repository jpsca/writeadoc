from docstring_parser.common import DocstringParam

from writeadoc.autodoc import Autodoc


class SimpleClass:
    """Simple test class.

    This is a longer description of the class.

    Attributes:
        attr1: First attribute.
        attr2: Second attribute.
    """

    def __init__(self, param1, param2=None):
        """Initialize the class.

        Args:
            param1: First parameter.
            param2: Second parameter, optional.
        """
        self.param1 = param1
        self.param2 = param2
        self._private = "private"

    def method(self, x, y=0):
        """A test method.

        Args:
            x: X parameter.
            y: Y parameter, defaults to 0.

        Returns:
            The sum of x and y.

        Raises:
            ValueError: If x is negative.
        """
        if x < 0:
            raise ValueError("x cannot be negative")
        return x + y

    @property
    def prop(self):
        """A test property.

        Returns:
            A string representation of param1.
        """
        return str(self.param1)


def sample_function(a, b=1, *, c=2):
    """Sample function for testing.

    Args:
        a: First parameter.
        b: Second parameter, defaults to 1.
        c: Keyword-only parameter, defaults to 2.

    Returns:
        The sum of all parameters.

    Examples:
        >>> sample_function(1, 2, c=3)
        6

    Deprecated:
        Use another_function instead.
    """
    return a + b + c


# Simple renderer that returns input as-is
autodoc = Autodoc()


def test_autodoc_parse_function():
    """Test autodoc_function function."""
    doc = autodoc("tests.test_autodoc.sample_function")

    assert doc.name == "sample_function"
    assert doc.symbol == "function"
    assert doc.short_description == "Sample function for testing."
    assert "Args:" not in doc.description
    assert len(doc.params) == 3
    assert doc.params[0].name == "a"
    assert doc.params[1].name == "b"
    assert doc.params[2].name == "c"
    assert len(doc.examples) == 1
    assert doc.returns is not None


def test_autodoc_parse_class():
    """Test autodoc_class function."""
    doc = autodoc("tests.test_autodoc.SimpleClass")

    assert doc.name == "SimpleClass"
    assert doc.symbol == "class"
    assert doc.short_description == "Simple test class."
    assert "longer description" in doc.long_description

    # Check attributes
    assert len(doc.attrs) == 2
    assert doc.attrs[0].name == "attr1"
    assert doc.attrs[1].name == "attr2"

    # Check methods
    assert len(doc.methods) == 1
    method = doc.methods[0]
    assert method.name == "method"
    assert method.symbol == "method"
    assert len(method.params) == 2

    # Check properties
    assert len(doc.properties) == 1
    prop = doc.properties[0]
    assert prop.name == "prop"
    assert prop.symbol == "attr"
    assert prop.label == "property"

    # Ensure private methods and attributes are excluded
    for method in doc.methods:
        assert not method.name.startswith("_")


def test_autodoc_function():
    """Test autodoc_function function."""
    doc = autodoc.autodoc_function(sample_function)

    assert doc.name == "sample_function"
    assert doc.symbol == "function"
    assert doc.short_description == "Sample function for testing."
    assert "Args:" not in doc.description
    assert len(doc.params) == 3
    assert doc.params[0].name == "a"
    assert doc.params[1].name == "b"
    assert doc.params[2].name == "c"
    assert len(doc.examples) == 1
    assert doc.returns is not None


def test_autodoc_class():
    """Test autodoc_class function."""
    doc = autodoc.autodoc_class(SimpleClass)

    assert doc.name == "SimpleClass"
    assert doc.symbol == "class"
    assert doc.short_description == "Simple test class."
    assert "longer description" in doc.long_description

    # Check attributes
    assert len(doc.attrs) == 2
    assert doc.attrs[0].name == "attr1"
    assert doc.attrs[1].name == "attr2"

    # Check methods
    assert len(doc.methods) == 1
    method = doc.methods[0]
    assert method.name == "method"
    assert method.symbol == "method"
    assert len(method.params) == 2

    # Check properties
    assert len(doc.properties) == 1
    prop = doc.properties[0]
    assert prop.name == "prop"
    assert prop.symbol == "attr"
    assert prop.label == "property"

    # Ensure private methods and attributes are excluded
    for method in doc.methods:
        assert not method.name.startswith("_")


def test_autodoc_property():
    """Test autodoc_property function."""
    doc = autodoc.autodoc_property("prop", SimpleClass.prop)

    assert doc.name == "prop"
    assert doc.symbol == "attr"
    assert doc.label == "property"
    assert "test property" in doc.short_description
    assert doc.returns is not None


def test_autodoc_attr():
    """Test autodoc_attr function."""
    param = DocstringParam(
        args=["param"],
        arg_name="test_param",
        type_name="str",
        description="A test parameter with a long description.\n\nMultiple paragraphs.",
        is_optional=False,
        default=None
    )

    doc = autodoc.autodoc_attr(param)

    assert doc.name == "test_param: str"
    assert doc.symbol == "attr"
    assert doc.label == "attribute"
    assert doc.short_description == "A test parameter with a long description."
    assert doc.long_description == "Multiple paragraphs."


def test_get_signature():
    """Test get_signature function."""
    # Test simple signature
    sig = autodoc.get_signature("simple", lambda x: x)
    assert sig == "simple(x)"

    # Test complex signature
    sig = autodoc.get_signature("complex", sample_function)
    print(sig)
    assert sig == """
complex(
    a,
    b=1,
    *,
    c=2
)""".strip()

    # Test signature with self parameter
    sig = autodoc.get_signature("method", SimpleClass.method)
    print(sig)
    assert sig == """
method(
    x,
    y=0
)""".strip()


def test_split_description():
    """Test split_description function."""
    # Single paragraph
    short, long = autodoc.split_description("Single paragraph.")
    assert short == "Single paragraph."
    assert long == ""

    # Multiple paragraphs
    short, long = autodoc.split_description("First paragraph.\n\nSecond paragraph.\n\nThird paragraph.")
    assert short == "First paragraph."
    assert long == "Second paragraph.\n\nThird paragraph."


def test_autodoc_full_path():
    """Test autodoc function that imports by path."""
    # Import a module from the standard library to test
    doc = autodoc("os.path.join")

    assert doc.name == "join"
    assert doc.symbol == "function"
    assert isinstance(doc.signature, str)
    assert "join" in doc.signature


def test_autodoc_obj():
    """Test autodoc_obj function with different types."""
    # Class
    class_doc = autodoc.autodoc_obj(SimpleClass)
    assert class_doc.name == "SimpleClass"
    assert class_doc.symbol == "class"

    # Function
    func_doc = autodoc.autodoc_obj(sample_function)
    assert func_doc.name == "sample_function"
    assert func_doc.symbol == "function"

    # Other object (should return empty Autodoc)
    other_doc = autodoc.autodoc_obj(42)
    assert other_doc.name == ""
    assert other_doc.symbol == ""


def test_docstring_special_attributes():
    """Test handling of special docstring attributes like example and return values."""
    doc = autodoc.autodoc_function(sample_function)

    # Check for examples
    assert len(doc.examples) == 1
    assert doc.examples[0].description is not None

    # Check for return values
    assert doc.returns is not None
    assert doc.returns.description is not None

    # Create a function with raises
    def raises_func():
        """Function that raises exceptions.

        Raises:
            ValueError: For invalid values.
            TypeError: For incorrect types.
        """
        pass

    doc = autodoc.autodoc_function(raises_func)
    assert len(doc.raises) == 2
    assert any(r.type_name == "ValueError" for r in doc.raises)
    assert any(r.type_name == "TypeError" for r in doc.raises)
