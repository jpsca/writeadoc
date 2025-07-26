import re
from html.parser import HTMLParser

from .types import TSearchData, PageData


def extract_search_data(pages) -> TSearchData:
    """
    Extract search data from processed pages.

    Args:
        pages: List of processed pages.

    Returns:
        SearchData object containing the search data.
    """
    data = {}
    for _, sec_pages in pages:
        for page in sec_pages:
            docs = extract_search_data_from_page(page)
            data.update(docs)

    return data


def extract_search_data_from_page(page: PageData) -> TSearchData:
    """
    Extract search data from a single page.

    Args:
        page: The page to extract data from.

    Returns:
        SearchData object containing the search data.
    """
    parser = TextExtractor(page)
    parser.feed(page.content)
    parser.close()
    return parser.docs




FRAGMENT_SIZE = 240

HTML_IGNORE = (
    "button",
    "dialog",
    "form",
    "iframe",
    "input",
    "nav",
    "script",
    "select",
    "style",
    "svg",
    "template",
    "textarea",
    "video",
)

HTML_HEADER_TAGS = (
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
)

HTML_BLOCK_TAGS = [
    "address",
    "article",
    "aside",
    "blockquote",
    "canvas",
    "dd",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    *HTML_HEADER_TAGS,
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "noscript",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tfoot",
    "ul",
    "video",
]

RX_MULTIPLE_SPACES = re.compile(r"\s+")
RX_NON_TEXT = re.compile(
    r"[^\w./_\-]|\s[._-]+|[._-]+\s|[._-]+$|^[._-]+|\s/\s",
    re.UNICODE | re.IGNORECASE,
)


class TextExtractor(HTMLParser):
    docs: TSearchData
    _capture: bool = True

    _page: PageData
    _fragment_size: int
    _overlap_size: int
    _hash: str
    _title: list[str]
    _content: list[str]
    _id: int

    def __init__(self, page: PageData, fragment_size: int = FRAGMENT_SIZE):
        super().__init__()
        self.docs = {}
        self._page = page
        self._fragment_size = fragment_size
        self._overlap_size = fragment_size // 20
        self._hash = ""
        self._title = []
        self._content = []
        self._id = 1

    @property
    def content(self) -> str:
        return RX_MULTIPLE_SPACES.sub(" ", "".join(self._content).strip())

    def handle_starttag(self, tag: str, attrs: list):
        if not self._capture:
            return

        if tag in HTML_IGNORE:
            self._capture = False
            return

        if tag in HTML_HEADER_TAGS:
            if "id" in dict(attrs):
                self._hash = dict(attrs)["id"]

    def handle_endtag(self, tag: str):
        if not self._capture:
            return

        if tag in HTML_BLOCK_TAGS:
            self._content.append(" ")

        if tag in HTML_IGNORE:
            self._capture = True
            return

    def handle_data(self, data: str):
        if not self._capture:
            return

        data = (
            data
            .replace("\n", "")
            .replace("&para;", "")
            .replace("¶", "")
            .replace(">", "&gt;")
            .replace("<", "&lt;")
        )
        data = RX_MULTIPLE_SPACES.sub(" ", data)
        if data:
            self._content.append(f"{data}")

        if len(self.content) > self._fragment_size:
            self.save_fragment()

    def save_fragment(self):
        content = self.content
        if not content or len(content) <= self._overlap_size:
            return

        title = "".join(self._title).strip()
        title = RX_MULTIPLE_SPACES.sub(" ", title)
        if not title:
            title = self._page.title

        url = self._page.url
        if self._hash:
            url = f"{self._page.url}#{self._hash}"

        self.docs[f"{self._page.id}-{self._id}"] = {
            "title": title,
            "content": content,
            "section": self._page.url,
            "url": url,
        }

        # store a part of the content for the next fragment
        # so they overlap
        overlap = content[-self._overlap_size:]
        # split and discard the first word because it was cut off
        overlap = overlap.split(" ")[1:]
        # add the missing spaces and store it
        self._content = [f"{word} " for word in overlap]
        self._id += 1

    def close(self):
        if self._content:
            self.save_fragment()
        super().close()
