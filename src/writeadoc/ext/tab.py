"""
Tab Block extension for Markdown.

Original code Copyright 2008-2024 The Python Markdown Project
https://github.com/facelessuser/pymdown-extensions/blob/main/pymdownx/blocks/tab.py
Used under the MIT License
"""

import xml.etree.ElementTree as etree

from markdown.treeprocessors import Treeprocessor
from pymdownx.blocks import BlocksExtension
from pymdownx.blocks.block import Block, type_boolean


HEADERS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class TabbedTreeprocessor(Treeprocessor):
    """Tab tree processor."""

    def run(self, doc):
        # Get a list of id attributes
        used_ids = set()
        for el in doc.iter():
            if "id" in el.attrib:
                used_ids.add(el.attrib["id"])


class Tab(Block):
    """
    Tabbed container.

    Arguments:
        - A tab title.

    Options:
        - `new` (boolean): since consecutive tabs are automatically grouped, `new` can force a tab
        to start a new tab container.

    Content:
        Detail body.
    """

    NAME = "tab"

    ARGUMENT = True
    OPTIONS = {"new": (False, type_boolean), "select": (False, type_boolean)}

    def on_init(self):
        """Handle initialization."""

        # Track tab group count across the entire page.
        if "tab_group_count" not in self.tracker:
            self.tracker["tab_group_count"] = 0

        self.tab_content = None

    def last_child(self, parent):
        """Return the last child of an `etree` element."""

        if len(parent):
            return parent[-1]
        else:
            return None

    def on_add(self, block):
        """Adjust where the content is added."""

        if self.tab_content is None:
            for d in block.findall("div"):
                c = d.attrib["class"]
                if c == "tabbed-content" or c.startswith("tabbed-content "):
                    self.tab_content = list(d)[-1]
                    break

        return self.tab_content

    def on_create(self, parent):
        """Create the element."""

        new_group = self.options["new"]
        select = self.options["select"]
        title = self.argument
        sibling = self.last_child(parent)
        tabbed_set = "tabbed-set"
        index = 0
        labels = None
        content = None

        if (
            sibling is not None
            and sibling.tag.lower() == "div"
            and sibling.attrib.get("class", "") == tabbed_set
            and not new_group
        ):
            first = False
            tab_group = sibling

            index = [index for index, _ in enumerate(tab_group.findall("input"), 1)][-1]
            for d in tab_group.findall("div"):
                if d.attrib["class"] == "tabbed-labels":
                    labels = d
                elif d.attrib["class"] == "tabbed-content":
                    content = d
                if labels is not None and content is not None:
                    break
        else:
            first = True
            self.tracker["tab_group_count"] += 1
            tab_group = etree.SubElement(
                parent,
                "div",
                {
                    "class": tabbed_set,
                    "data-tabs": "%d:0" % self.tracker["tab_group_count"],
                },
            )
            labels = etree.SubElement(tab_group, "div", {"class": "tabbed-labels"})
            content = etree.SubElement(tab_group, "div", {"class": "tabbed-content"})

        data = tab_group.attrib["data-tabs"].split(":")
        tab_set = int(data[0])
        tab_count = int(data[1]) + 1

        attributes = {
            "name": "__tabbed_%d" % tab_set,
            "type": "radio",
            "id": "__tabbed_%d_%d" % (tab_set, tab_count),
        }
        attributes2 = {"for": "__tabbed_%d_%d" % (tab_set, tab_count)}

        if first or select:
            attributes["checked"] = "checked"
            # Remove any previously assigned "checked states" to siblings
            for i in tab_group.findall("input"):
                if i.attrib.get("name", "") == f"__tabbed_{tab_set}":
                    if "checked" in i.attrib:
                        del i.attrib["checked"]

        input_el = etree.Element("input", attributes)
        tab_group.insert(index, input_el)
        lab = etree.SubElement(labels, "label", attributes2)  # type: ignore
        lab.text = title
        attrib = {"class": "tabbed-block"}
        etree.SubElement(content, "div", attrib)  # type: ignore

        tab_group.attrib["data-tabs"] = "%d:%d" % (tab_set, tab_count)

        return tab_group


class TabExtension(BlocksExtension):
    """Tab Block Extension."""

    def extendMarkdownBlocks(self, md, block_mgr):
        block_mgr.register(Tab, self.getConfigs())


def makeExtension(*args, **kwargs):
    """Return extension."""

    return TabExtension(*args, **kwargs)
