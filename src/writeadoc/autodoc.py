import inspect
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


@dataclass(slots=True)
class Autodoc:
    name: str = ""
    symbol: str = ""
    label: str = ""
    signature: str = ""
    params: list["Autodoc"] = field(default_factory=list)

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
    attrs: list["Autodoc"] = field(default_factory=list)
    # Properties
    properties: list["Autodoc"] = field(default_factory=list)
    # Methods
    methods: list["Autodoc"] = field(default_factory=list)



def autodoc(name: str) -> Autodoc:
    module_name, obj_name = name.rsplit(".", 1)
    module = import_module(module_name)
    assert module
    obj = getattr(module, obj_name, None)
    assert obj
    return autodoc_obj(obj)


def autodoc_obj(obj: t.Any) -> Autodoc:
    if inspect.isclass(obj):
        return autodoc_class(obj)
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        return autodoc_function(obj)
    else:
        return Autodoc()


def autodoc_class(obj: t.Any, *, symbol: str = "class") -> Autodoc:
    init = getattr(obj, "__init__", None)
    obj_name = obj.__name__
    ds = obj.__doc__ or init.__doc__ or ""
    parsed_ds = parse(ds)

    description = (parsed_ds.description or "").strip()
    short_description, long_description = split_description(description)

    params = []
    attrs = []
    properties = []
    methods = []

    for param in parsed_ds.params:
        doc = autodoc_attr(param)
        if param.args[0] == "param":
            params.append(doc)
        elif param.args[0] == "attribute":
            attrs.append(doc)

    for name, value in  inspect.getmembers(obj):
        if name[0] == "_":
            continue
        if inspect.isfunction(value):
            methods.append(autodoc_function(value, symbol="method"))
            continue
        if isinstance(value, property):
            properties.append(autodoc_property(name, value))
            continue

    return Autodoc(
        symbol=symbol,
        name=obj_name,
        signature=get_signature(obj_name, init),
        params=params,
        short_description=short_description,
        long_description=long_description,
        description=description,
        deprecation=parsed_ds.deprecation,
        returns=parsed_ds.returns,
        raises=parsed_ds.raises,
        examples=parsed_ds.examples,
        many_returns=parsed_ds.many_returns,

        bases=[
            base.__name__ for base in obj.__bases__
            if base.__name__ != "object"
        ],
        attrs=attrs,
        properties=properties,
        methods=methods,
    )


def autodoc_function(obj: t.Any, *, symbol: str = "function") -> Autodoc:
    obj_name = obj.__name__
    parsed_ds = parse(obj.__doc__ or "")

    description = (parsed_ds.description or "").strip()
    short_description, long_description = split_description(description)
    params = [autodoc_attr(param) for param in parsed_ds.params]

    return Autodoc(
        name=obj_name,
        symbol=symbol,
        signature=get_signature(obj_name, obj),
        params=params,
        short_description=short_description,
        long_description=long_description,
        description=description,
        deprecation=parsed_ds.deprecation,
        returns=parsed_ds.returns,
        raises=parsed_ds.raises,
        examples=parsed_ds.examples,
        many_returns=parsed_ds.many_returns,
    )


def autodoc_property(name: str, obj: t.Any, *, symbol: str = "attr") -> Autodoc:
    parsed_ds = parse(obj.__doc__ or "")

    description = (parsed_ds.description or "").strip()
    short_description, long_description = split_description(description)

    return Autodoc(
        name=name,
        symbol=symbol,
        label="property",
        short_description=short_description,
        long_description=long_description,
        description=description,
        deprecation=parsed_ds.deprecation,
        returns=parsed_ds.returns,
        raises=parsed_ds.raises,
        examples=parsed_ds.examples,
        many_returns=parsed_ds.many_returns,
    )


def autodoc_attr(attr: DocstringParam, *, symbol: str = "attr") -> Autodoc:
    if attr.type_name:
        name = f"{attr.arg_name}: {attr.type_name}"
    else:
        name = attr.arg_name

    description = (attr.description or "").strip()
    short_description, long_description = split_description(description)

    return Autodoc(
        symbol=symbol,
        name=name,
        label="attribute",
        short_description=short_description,
        long_description=long_description,
        description=description,
    )


def get_signature(obj_name: str, obj: t.Any, split_at: int = 70) -> str:
    sig = inspect.signature(obj)
    str_sig = str(sig).replace("(self, ", "(").replace("(self)", "()")
    fullsig = f"{obj_name}{str_sig}"
    if len(fullsig) < split_at:
        return fullsig

    fullsig = (
        fullsig
        .replace("*, ", "\n    *, ")
        .replace(", **", ",\n    **")
        .replace("(", "(\n    ", 1)
    )
    for name in sig.parameters:
        fullsig = fullsig.replace(f", {name}", f",\n    {name}")

    return fullsig.replace(") ->", "\n) ->")


def split_description(description: str) -> tuple[str, str]:
    if "\n\n" not in description:
        return description, ""
    head, rest = description.split("\n\n", 1)
    return head, rest
