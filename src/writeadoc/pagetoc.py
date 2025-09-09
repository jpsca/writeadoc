"""
Custom Table of Contents extension for Markdown.
Extended to support skipping headers with a `skip-toc` attribute
and to remove the HTML generation.

Original code Copyright 2008 [Jack Miller](https://codezen.org/)
Python-Markdown changes Copyright 2008-2024 The Python Markdown Project
License: [BSD](https://opensource.org/licenses/bsd-license.php)
"""

import html
import re
import unicodedata
import xml.etree.ElementTree as etree
from collections.abc import MutableSet
from copy import deepcopy
from typing import Any

from markdown import Markdown
from markdown.extensions import Extension
from markdown.serializers import RE_AMP
from markdown.treeprocessors import Treeprocessor, UnescapeTreeprocessor
from markdown.util import (
    AMP_SUBSTITUTE,
    parseBoolValue,
)


def slugify(value: str, separator: str, unicode: bool = False) -> str:
    """Slugify a string, to make it URL friendly."""
    if not unicode:
        # Replace Extended Latin characters with ASCII, i.e. `žlutý` => `zluty`
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[{}\s]+".format(separator), separator, value)


def slugify_unicode(value: str, separator: str) -> str:
    """Slugify a string, to make it URL friendly while preserving Unicode characters."""
    return slugify(value, separator, unicode=True)


IDCOUNT_RE = re.compile(r"^(.*)_([0-9]+)$")


def unique(id: str, ids: MutableSet[str]) -> str:
    """Ensure id is unique in set of ids. Append '_1', '_2'... if not"""
    while id in ids or not id:
        m = IDCOUNT_RE.match(id)
        if m:
            id = "%s_%d" % (m.group(1), int(m.group(2)) + 1)
        else:
            id = "%s_%d" % (id, 1)
    ids.add(id)
    return id


def unescape(text: str) -> str:
    """Unescape Markdown backslash escaped text."""
    c = UnescapeTreeprocessor()
    return c.unescape(text)


def strip_tags(text: str) -> str:
    """Strip HTML tags and return plain text. Note: HTML entities are unaffected."""
    # A comment could contain a tag, so strip comments first
    while (start := text.find("<!--")) != -1 and (end := text.find("-->", start)) != -1:
        text = f"{text[:start]}{text[end + 3 :]}"

    while (start := text.find("<")) != -1 and (end := text.find(">", start)) != -1:
        text = f"{text[:start]}{text[end + 1 :]}"

    # Collapse whitespace
    text = " ".join(text.split())
    return text


def escape_cdata(text: str) -> str:
    """Escape character data."""
    if "&" in text:
        # Only replace & when not part of an entity
        text = RE_AMP.sub("&amp;", text)
    if "<" in text:
        text = text.replace("<", "&lt;")
    if ">" in text:
        text = text.replace(">", "&gt;")
    return text


def run_postprocessors(text: str, md: Markdown) -> str:
    """Run postprocessors from Markdown instance on text."""
    for pp in md.postprocessors:
        text = pp.run(text)
    return text.strip()


def render_inner_html(el: etree.Element, md: Markdown) -> str:
    """Fully render inner html of an `etree` element as a string."""
    # The `UnescapeTreeprocessor` runs after `toc` extension so run here.
    text = unescape(md.serializer(el))

    # strip parent tag
    start = text.index(">") + 1
    end = text.rindex("<")
    text = text[start:end].strip()

    return run_postprocessors(text, md)


def remove_fnrefs(root: etree.Element) -> etree.Element:
    """Remove footnote references from a copy of the element, if any are present."""
    # Remove footnote references, which look like this: `<sup id="fnref:1">...</sup>`.
    # If there are no `sup` elements, then nothing to do.
    if next(root.iter("sup"), None) is None:
        return root
    root = deepcopy(root)
    # Find parent elements that contain `sup` elements.
    for parent in root.findall(".//sup/.."):
        carry_text = ""
        for child in reversed(
            parent
        ):  # Reversed for the ability to mutate during iteration.
            # Remove matching footnote references but carry any `tail` text to preceding elements.
            if child.tag == "sup" and child.get("id", "").startswith("fnref"):
                carry_text = f"{child.tail or ''}{carry_text}"
                parent.remove(child)
            elif carry_text:
                child.tail = f"{child.tail or ''}{carry_text}"
                carry_text = ""
        if carry_text:
            parent.text = f"{parent.text or ''}{carry_text}"
    return root


def nest_toc_tokens(toc_list):
    """Given an unsorted list with errors and skips, return a nested one.

        [{'level': 1}, {'level': 2}]
        =>
        [{'level': 1, 'children': [{'level': 2, 'children': []}]}]

    A wrong list is also converted:

        [{'level': 2}, {'level': 1}]
        =>
        [{'level': 2, 'children': []}, {'level': 1, 'children': []}]
    """

    ordered_list = []
    if len(toc_list):
        # Initialize everything by processing the first entry
        last = toc_list.pop(0)
        last["children"] = []
        levels = [last["level"]]
        ordered_list.append(last)
        parents = []

        # Walk the rest nesting the entries properly
        while toc_list:
            t = toc_list.pop(0)
            current_level = t["level"]
            t["children"] = []

            # Reduce depth if current level < last item's level
            if current_level < levels[-1]:
                # Pop last level since we know we are less than it
                levels.pop()

                # Pop parents and levels we are less than or equal to
                to_pop = 0
                for p in reversed(parents):
                    if current_level <= p["level"]:
                        to_pop += 1
                    else:  # pragma: no cover
                        break
                if to_pop:
                    levels = levels[:-to_pop]
                    parents = parents[:-to_pop]

                # Note current level as last
                levels.append(current_level)

            # Level is the same, so append to
            # the current parent (if available)
            if current_level == levels[-1]:
                (parents[-1]["children"] if parents else ordered_list).append(t)

            # Current level is > last item's level,
            # So make last item a parent and append current as child
            else:
                last["children"].append(t)
                parents.append(last)
                levels.append(current_level)
            last = t

    return ordered_list


class TocTreeprocessor(Treeprocessor):
    """Step through document and build TOC."""

    def __init__(self, md: Markdown, config: dict[str, Any]):
        super().__init__(md)

        self.title: str = config["title"]
        self.base_level = int(config["baselevel"]) - 1
        self.slugify = config["slugify"]
        self.sep = config["separator"]
        self.toc_class = config["toc_class"]
        self.title_class: str = config["title_class"]
        self.use_anchors: bool = parseBoolValue(config["anchorlink"])  # type: ignore
        self.anchorlink_class: str = config["anchorlink_class"]
        self.use_permalinks = parseBoolValue(config["permalink"], False)
        if self.use_permalinks is None:
            self.use_permalinks = config["permalink"]
        self.permalink_class: str = config["permalink_class"]
        self.permalink_title: str = config["permalink_title"]
        self.permalink_leading: bool | None = parseBoolValue(
            config["permalink_leading"], False
        )
        self.header_rgx = re.compile("[Hh][123456]")
        if isinstance(config["toc_depth"], str) and "-" in config["toc_depth"]:
            self.toc_top, self.toc_bottom = [
                int(x) for x in config["toc_depth"].split("-")
            ]
        else:
            self.toc_top = 1
            self.toc_bottom = int(config["toc_depth"])

    def set_level(self, elem: etree.Element) -> None:
        """Adjust header level according to base level."""
        level = int(elem.tag[-1]) + self.base_level
        if level > 6:
            level = 6
        elem.tag = "h%d" % level

    def add_anchor(self, c: etree.Element, elem_id: str) -> None:
        anchor = etree.Element("a")
        anchor.text = c.text
        anchor.attrib["href"] = "#" + elem_id
        anchor.attrib["class"] = self.anchorlink_class
        c.text = ""
        for elem in c:
            anchor.append(elem)
        while len(c):
            c.remove(c[0])
        c.append(anchor)

    def add_permalink(self, c: etree.Element, elem_id: str) -> None:
        permalink = etree.Element("a")
        permalink.text = (
            f"{AMP_SUBSTITUTE}para;"
            if self.use_permalinks is True
            else self.use_permalinks
        )  # type: ignore
        permalink.attrib["href"] = "#" + elem_id
        permalink.attrib["class"] = self.permalink_class
        if self.permalink_title:
            permalink.attrib["title"] = self.permalink_title
        if self.permalink_leading:
            permalink.tail = c.text
            c.text = ""
            c.insert(0, permalink)
        else:
            c.append(permalink)

    def run(self, doc: etree.Element) -> None:
        # Get a list of id attributes
        used_ids = set()
        for el in doc.iter():
            if "id" in el.attrib:
                used_ids.add(el.attrib["id"])

        toc_tokens = []
        for el in doc.iter():
            if isinstance(el.tag, str) and self.header_rgx.match(el.tag):
                if "skip-toc" in el.attrib:
                    continue

                self.set_level(el)
                innerhtml = render_inner_html(remove_fnrefs(el), self.md)
                name = strip_tags(innerhtml)

                # Do not override pre-existing ids
                if "id" not in el.attrib:
                    el.attrib["id"] = unique(
                        self.slugify(html.unescape(name), self.sep), used_ids
                    )

                if int(el.tag[-1]) >= self.toc_top and int(el.tag[-1]) <= self.toc_bottom:
                    toc_tokens.append(
                        {
                            "level": int(el.tag[-1]),
                            "id": unescape(el.attrib["id"]),
                            "name": name,
                            "html": innerhtml,
                        }
                    )

                if self.use_anchors:
                    self.add_anchor(el, el.attrib["id"])
                if self.use_permalinks not in [False, None]:
                    self.add_permalink(el, el.attrib["id"])

        toc_tokens = nest_toc_tokens(toc_tokens)
        self.md.toc_tokens = toc_tokens  # type: ignore


class TocExtension(Extension):
    TreeProcessorClass = TocTreeprocessor

    def __init__(self, **kwargs):
        self.config = {
            "title": ["", "Title to insert into TOC `<div>`. Default: an empty string."],
            "title_class": [
                "toctitle",
                "CSS class used for the title. Default: `toctitle`.",
            ],
            "toc_class": ["toc", "CSS class(es) used for the link. Default: `toclink`."],
            "anchorlink": [
                False,
                "True if header should be a self link. Default: `False`.",
            ],
            "anchorlink_class": [
                "toclink",
                "CSS class(es) used for the link. Defaults: `toclink`.",
            ],
            "permalink": [
                True,
                "True or link text if a Sphinx-style permalink should be added. Default: `False`.",
            ],
            "permalink_class": [
                "headerlink",
                "CSS class(es) used for the link. Default: `headerlink`.",
            ],
            "permalink_title": [
                "Permanent link",
                "Title attribute of the permalink. Default: `Permanent link`.",
            ],
            "permalink_leading": [
                False,
                "True if permalinks should be placed at start of the header, rather than end. Default: False.",
            ],
            "baselevel": ["1", "Base level for headers. Default: `1`."],
            "slugify": [
                slugify,
                "Function to generate anchors based on header text. Default: `slugify`.",
            ],
            "separator": ["-", "Word separator. Default: `-`."],
            "toc_depth": [
                "1-3",
                "Define the range of section levels to include in the Table of Contents. A single integer "
                "(b) defines the bottom section level (<h1>..<hb>) only. A string consisting of two digits "
                "separated by a hyphen in between (`2-5`) defines the top (t) and the bottom (b) (<ht>..<hb>). "
                "Default: `6` (bottom).",
            ],
        }
        """ Default configuration options. """

        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.registerExtension(self)
        self.md = md
        self.reset()
        tocext = self.TreeProcessorClass(md, self.getConfigs())
        md.treeprocessors.register(tocext, "pagetoc", 5)

    def reset(self) -> None:
        self.md.toc_tokens = []  # type: ignore


def makeExtension(**kwargs):  # pragma: no cover
    return TocExtension(**kwargs)
