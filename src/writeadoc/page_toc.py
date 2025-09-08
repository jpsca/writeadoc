"""
Custom Table of Contents extension for Markdown.

Extended to support skipping headers with a 'skip-toc' attribute.
"""
import html
import xml.etree.ElementTree as etree

from markdown.extensions.toc import (
    TocExtension,
    TocTreeprocessor,
    nest_toc_tokens,
    remove_fnrefs,
    render_inner_html,
    strip_tags,
    unescape,
    unique,
)


class PageTocTreeprocessor(TocTreeprocessor):
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

                if self.use_anchors:
                    self.add_anchor(el, el.attrib["id"])
                if self.use_permalinks not in [False, None]:
                    self.add_permalink(el, el.attrib["id"])

                if int(el.tag[-1]) >= self.toc_top and int(el.tag[-1]) <= self.toc_bottom:
                    toc_tokens.append(
                        {
                            "level": int(el.tag[-1]),
                            "id": unescape(el.attrib["id"]),
                            "name": name,
                            "html": innerhtml,
                        }
                    )

        toc_tokens = nest_toc_tokens(toc_tokens)
        div = self.build_toc_div(toc_tokens)
        if self.marker:
            self.replace_marker(doc, div)

        self.md.toc_tokens = toc_tokens  # type: ignore


class PageTocExtension(TocExtension):
    TreeProcessorClass = PageTocTreeprocessor
