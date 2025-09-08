import re
from html.parser import HTMLParser

from .types import PageData, TSearchData


def extract_search_data(page: PageData) -> TSearchData:
    """
    Extract search data from a single page.

    Arguments:
        page: The page to extract data from.

    Returns:
        SearchData object containing the search data.
    """
    parser = TextExtractor(page)
    html = prepare_html(page.content)
    if not html:
        return {}
    parser.feed(html)
    parser.close()
    return parser.docs


REMOVE_SELF_CLOSING_TAGS = (
    "hr",
    "input",
    "img",
    "link",
    "meta",
    "source",
    "track",
    "wbr",
    "area",
    "base",
    "col",
    "command",
    "embed",
)

REMOVE_TAGS_AND_CONTENTS = (
    "button",
    "canvas",
    "dialog",
    "form",
    "iframe",
    "nav",
    "noscript",
    "script",
    "select",
    "style",
    "svg",
    "template",
    "textarea",
    "video",
)

REMOVE_TAGS_KEEP_CONTENT = (
    "a",
    "address",
    "article",
    "aside",
    "b",
    "code",
    "div",
    "em",
    "fieldset",
    "figure",
    "footer",
    "figcaption",
    "header",
    "i",
    "kbd",
    "main",
    "mark",
    "samp",
    "section",
    "span",
    "strong",
    "tfoot",
)

HTML_HEADER = (
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
)

HTML_PRE = "pre"

HTML_FRAGMENT_SEP = (
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "pre",
    "table",
)

RX_MULTIPLE_SPACES = re.compile(r"\s+")


def prepare_html(html: str) -> str:
    """
    Prepare HTML content by removing unwanted tags and contents.

    Arguments:
        html: The HTML content to prepare.

    Returns:
        Cleaned HTML content.
    """
    if not html:
        return ""

    # Remove self-closing tags
    for tag in REMOVE_SELF_CLOSING_TAGS:
        html = re.sub(rf"<{tag}.*?/>", "", html, flags=re.DOTALL)
    # Remove tags and their contents
    for tag in REMOVE_TAGS_AND_CONTENTS:
        html = re.sub(rf"<{tag}.*?>.*?</{tag}>", "", html, flags=re.DOTALL)
    # Remove tags but keep their contents
    for tag in REMOVE_TAGS_KEEP_CONTENT:
        html = re.sub(rf"<{tag}.*?>(.*?)</{tag}>", r"\1", html, flags=re.DOTALL)

    html = html.strip()
    return html


class TextExtractor(HTMLParser):
    docs: TSearchData
    _tag: str = "p"
    _in_header: bool = False

    _page: PageData
    _fragment_size: int
    _overlap_size: int
    _hash: str
    _title: list[str]
    _content: list[str]
    _id: int

    def __init__(self, page: PageData):
        super().__init__()
        self.docs = {}
        self._page = page
        self._hash = ""
        self._title = []
        self._content = []
        self._id = 1

    def handle_starttag(self, tag: str, attrs: list):
        self._tag = tag

        if tag in HTML_FRAGMENT_SEP:
            if self._content:
                self.save_fragment()

        if tag in HTML_HEADER:
            self._title = []
            self._in_header = True
            if "id" in dict(attrs):
                self._hash = dict(attrs)["id"]
            return

    def handle_endtag(self, tag: str):
        if tag in HTML_HEADER:
            self._in_header = False
            return

    def handle_data(self, data: str):
        if self._tag == HTML_PRE:
            data = (
                data
                .replace("&", "&amp;")
                .replace(">", "&gt;")
                .replace("<", "&lt;")
            )
            if data.strip():
                self._content.append(f"<pre>{data}</pre>")
            return

        if self._in_header:
            data = (
                data
                .replace("&para;", "")
                .replace("&", "&amp;")
                .replace(">", "&gt;")
                .replace("<", "&lt;")
                .replace("¶", "")
                .replace("\n", "")
            )
            data = RX_MULTIPLE_SPACES.sub(" ", data)
            if data:
                self._title.append(data)
            return

        data = (
            data
            .replace("\n", "")
            .replace("&", "&amp;")
            .replace(">", "&gt;")
            .replace("<", "&lt;")
        )
        if data:
            data = RX_MULTIPLE_SPACES.sub(" ", data)
            self._content.append(data)

    def save_fragment(self):
        title = "".join(self._title).strip()
        title = RX_MULTIPLE_SPACES.sub(" ", title)
        if not title:
            title = self._page.title

        content = "".join(self._content)
        if not content or content == self._page.title:
            return

        url = self._page.url
        if self._hash:
            url = f"{self._page.url}#{self._hash}"

        self.docs[f"{url}{self._id}"] = {
            "title": title,
            "content": content,
            "section": self._page.section_title,
            "url": url,
        }
        self._content = []
        self._id += 1

    def close(self):
        if self._content:
            self.save_fragment()
        super().close()
