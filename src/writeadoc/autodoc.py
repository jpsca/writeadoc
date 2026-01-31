import inspect
import re
import typing as t
from dataclasses import dataclass, field
from importlib import import_module

from docstring_parser import parse
from docstring_parser.common import (
    DocstringDeprecated,
    DocstringExample,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
)


RX_AUTODOC = re.compile(
    r"^:::\s*api(\s*\|)?\s+(?P<name>[^\n]+)(?:\n|$)"
    r"(?P<options>(?:\:[a-zA-Z0-9_-]+\: *[^\n]*\n+)*)"
    r"^:::",
    re.MULTILINE,
)
RX_FENCED = re.compile(r"\n```+.*?\n[\s\S]*?\n```+\n", re.MULTILINE)


@dataclass(slots=True)
class AttrDocstring:
    symbol: str = ""
    name: str = ""
    label: str = "attribute"
    short_description: str = ""
    long_description: str = ""
    description: str = ""


@dataclass(slots=True)
class Docstring:
    name: str = ""
    symbol: str = ""
    label: str = ""
    signature: str = ""
    params: list[AttrDocstring] = field(default_factory=list)

    # First paragraph of the description
    short_description: str = ""
    # Rest of the description
    long_description: str = ""
    # The full description
    description: str = ""

    # Deprecation notes
    deprecation: DocstringDeprecated | None = None
    # A list of examples.
    examples: list[DocstringExample] = field(default_factory=list)
    # Return information.
    returns: DocstringReturns | None = None
    # A list of multiple return values.
    many_returns: list[DocstringReturns] = field(default_factory=list)
    # A list of exceptions that the function may raise.
    raises: list[DocstringRaises] = field(default_factory=list)

    # Inheritance information
    bases: list[str] = field(default_factory=list)
    # Attributes
    attrs: list[AttrDocstring] = field(default_factory=list)
    # Properties
    properties: list[AttrDocstring] = field(default_factory=list)
    # Methods
    methods: list["Docstring"] = field(default_factory=list)


def render_autodoc(source: str, *, render: t.Callable) -> str:
    blocks = find_autodocs_blocks(source)
    for block in reversed(blocks):
        level = int(block["options"].pop("level", 2))
        ds = autodoc(block["name"], **block["options"])
        frag = render(ds=ds, level=level)
        frag = str(frag).strip()
        start = block["start"]
        end = block["end"]
        source = f"{source[:start]}{frag}{source[end:]}"

    return source.strip()


def find_autodocs_blocks(source: str) -> list[dict[str, t.Any]]:
    # Find all ::: api ... blocks
    api_blocks = list(RX_AUTODOC.finditer(source))

    # Find all code fence regions
    code_fences = [m.span() for m in RX_FENCED.finditer(source)]

    def is_inside_code_fence(start, code_fences):
        return any(
            fence_start <= start < fence_end for fence_start, fence_end in code_fences
        )

    return [
        {
            "name": m.group("name").strip(),
            "options": parse_options(m),
            "start": m.start(),
            "end": m.end(),
        }
        for m in api_blocks
        if not is_inside_code_fence(m.start(), code_fences)
    ]


def parse_options(m: re.Match[str]) -> dict[str, str]:
    text = m.group("options")
    if not text.strip():
        return {}

    options = []
    for line in re.split(r"\n+", text):
        line = line.strip()[1:]
        if not line:
            continue

        i = line.find(":")
        k = line[:i]
        v = line[i + 1 :].strip()

        if v.lower() == "true":
            v = True
        elif v.lower() == "false":
            v = False
        elif v.isdigit():
            v = int(v)
        options.append((k, v))

    return dict(options)


def autodoc(
    name: str,
    *,
    show_members: bool = True,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> Docstring:
    module_name, obj_name = name.rsplit(".", 1)
    attr = None
    if ":" in obj_name:
        obj_name, attr = obj_name.split(":", 1)
    module = import_module(module_name)
    assert module
    obj = getattr(module, obj_name, None)
    if not obj:
        raise ValueError(f"Object {obj_name} not found in module {module_name}")
    if attr:
        obj = getattr(obj, attr, None)
        if not obj:
            raise ValueError(f"Attribute {attr} not found in object {obj_name}")

    return autodoc_obj(
        obj,
        show_members=show_members,
        include=include,
        exclude=exclude,
    )


def autodoc_obj(
    obj: t.Any,
    *,
    show_members: bool = True,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> Docstring:
    if inspect.isclass(obj):
        ds = autodoc_class(
            obj,
            show_members=show_members,
            include=include,
            exclude=exclude,
        )
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        ds = autodoc_function(obj)
    else:
        ds = Docstring()
    return ds


def autodoc_class(
    obj: t.Any,
    *,
    symbol: str = "class",
    show_members: bool = True,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> Docstring:
    init = getattr(obj, "__init__", None)
    obj_name = obj.__name__
    ds = parse(obj.__doc__ or init.__doc__ or "")

    description = (ds.description or "").strip()
    short_description, long_description = split_description(description)

    params = []
    attrs = []
    properties = []
    methods = []

    for param in ds.params:
        doc = autodoc_attr(param)
        if param.args[0] == "param":
            params.append(doc)
        elif param.args[0] == "attribute":
            attrs.append(doc)

    exclude_all = "*" in exclude
    if show_members:
        for name, value in inspect.getmembers(obj):
            if name.startswith("_") and name not in include:
                continue
            if (exclude_all or name in exclude) and name not in include:
                continue
            if inspect.isfunction(value):
                methods.append(autodoc_function(value))
                continue
            if isinstance(value, property):
                properties.append(autodoc_property(name, value))
                continue

    if ds.deprecation:
        ds.deprecation.description = (ds.deprecation.description or "").strip()
    if ds.returns:
        ds.returns.description = (ds.returns.description or "").strip()
    for meta in ds.raises:
        meta.description = (meta.description or "").strip()
    for meta in ds.many_returns:
        meta.description = (meta.description or "").strip()
    for meta in ds.examples:
        meta.snippet = (meta.snippet or "").strip()
        meta.description = (meta.description or "").strip()

    return Docstring(
        symbol=symbol,
        name=obj_name,
        signature=get_signature(obj_name, init),
        params=params,
        short_description=short_description,
        long_description=long_description,
        description=description,
        deprecation=ds.deprecation,
        returns=ds.returns,
        raises=ds.raises,
        examples=ds.examples,
        many_returns=ds.many_returns,
        bases=[base.__name__ for base in obj.__bases__ if base.__name__ != "object"],
        attrs=attrs,
        properties=properties,
        methods=methods,
    )


def autodoc_function(
    obj: t.Any,
    *,
    symbol: str = "",
) -> Docstring:
    obj_name = obj.__name__
    ds = parse(obj.__doc__ or "")

    description = (ds.description or "").strip()
    short_description, long_description = split_description(description)
    params = [autodoc_attr(param) for param in ds.params]

    if ds.deprecation:
        ds.deprecation.description = (ds.deprecation.description or "").strip()
    if ds.returns:
        ds.returns.description = (ds.returns.description or "").strip()
    for meta in ds.raises:
        meta.description = (meta.description or "").strip()
    for meta in ds.many_returns:
        meta.description = (meta.description or "").strip()
    for meta in ds.examples:
        meta.snippet = (meta.snippet or "").strip()
        meta.description = (meta.description or "").strip()

    if not symbol:
        if inspect.ismethod(obj):
            symbol = "method"
        elif inspect.iscoroutinefunction(obj):
            symbol = "async function"
        else:
            symbol = "function"
    return Docstring(
        symbol=symbol,
        name=obj_name,
        signature=get_signature(obj_name, obj),
        params=params,
        short_description=short_description,
        long_description=long_description,
        description=description,
        deprecation=ds.deprecation,
        returns=ds.returns,
        raises=ds.raises,
        examples=ds.examples,
        many_returns=ds.many_returns,
    )


def autodoc_property(name: str, obj: t.Any, *, symbol: str = "attr") -> Docstring:
    ds = parse(obj.__doc__ or "")
    description = (ds.description or "").strip()
    short_description, long_description = split_description(description)

    return Docstring(
        name=name,
        symbol=symbol,
        label="property",
        short_description=short_description,
        long_description=long_description,
        description=description,
        deprecation=ds.deprecation,
        returns=ds.returns,
        raises=ds.raises,
        examples=ds.examples,
        many_returns=ds.many_returns,
    )


def autodoc_attr(attr: DocstringParam, *, symbol: str = "attr") -> AttrDocstring:
    if attr.type_name:
        name = f"{attr.arg_name}: {attr.type_name}"
    else:
        name = attr.arg_name

    description = (attr.description or "").strip()
    short_description, long_description = split_description(description)

    return AttrDocstring(
        symbol=symbol,
        name=name,
        label="attribute",
        short_description=short_description,
        long_description=long_description,
        description=description,
    )


RX_SELF = re.compile(r"\bself\b,?\s*")


def get_signature(obj_name: str, obj: t.Any, max_width: int = 10) -> str:
    sig = inspect.signature(obj)
    str_sig = format_signature(sig, max_width=max_width)
    str_sig = RX_SELF.sub("", str_sig)
    return f"{obj_name}{str_sig}"


def split_description(description: str) -> tuple[str, str]:
    if "\n\n" not in description:
        return description, ""
    head, rest = description.split("\n\n", 1)
    return head, rest


def format_signature(sig, *, max_width: int = -1) -> str:
    """Create a string representation of the Signature object.

    If *max_width* integer is passed, signature will try to fit into the *max_width*.
    If signature is longer than *max_width*, all parameters will be on separate lines.
    """
    result = []
    render_pos_only_separator = False
    render_kw_only_separator = True
    for param in sig.parameters.values():
        formatted = str(param)

        kind = str(param.kind).lower().replace("_", "-")
        if kind == "positional-only":
            render_pos_only_separator = True
        elif render_pos_only_separator:
            # It's not a positional-only parameter, and the flag
            # is set to 'True' (there were pos-only params before.)
            result.append("/")
            render_pos_only_separator = False

        if kind == "variadic positional":
            # OK, we have an '*args'-like parameter, so we won't need
            # a '*' to separate keyword-only arguments
            render_kw_only_separator = False
        elif kind == "keyword-only" and render_kw_only_separator:
            # We have a keyword-only parameter to render and we haven't
            # rendered an '*args'-like parameter before, so add a '*'
            # separator to the parameters list ("foo(arg1, *, arg2)" case)
            result.append("*")
            # This condition should be only triggered once, so
            # reset the flag
            render_kw_only_separator = False

        result.append(formatted)

    if render_pos_only_separator:
        # There were only positional-only parameters, hence the
        # flag was not reset to 'False'
        result.append("/")

    rendered = "({})".format(", ".join(result))
    if max_width > 0 and len(rendered) > max_width:
        rendered = "(\n    {}\n)".format(",\n    ".join(result))

    if sig.return_annotation is not inspect._empty:
        anno = inspect.formatannotation(sig.return_annotation)
        rendered += " -> {}".format(anno)

    return rendered
