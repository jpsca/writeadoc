import typing as t
from uuid import uuid4


class SectionRef(t.TypedDict):
    id: str
    title: str
    url: str


class PageRef(t.TypedDict):
    id: str
    title: str
    url: str


class SiteData:
    name: str
    description: str
    image: str
    version: str
    base_url: str
    source_url: str
    help_url: str
    pages: list[tuple[SectionRef, list[PageRef]]]

    def __init__(
        self,
        *,
        name: str = "WriteADoc",
        description: str = "",
        image: str = "/assets/images/opengraph.png",
        version: str = "0.1.0",
        base_url: str = "",
        source_url: str = "",
        help_url: str = "",
    ):
        self.name = name
        self.description = description
        self.image = image
        self.version = version
        self.base_url = base_url
        self.source_url = source_url
        self.help_url = help_url
        self.pages = []


class PageData:
    id: str
    section: SectionRef
    title: str
    url: str
    description: str
    image: str
    meta: dict[str, t.Any]
    content: str
    prev: PageRef | None = None
    next: PageRef | None = None

    def __init__(
        self,
        *,
        section: SectionRef,
        title: str,
        url: str,
        description: str = "",
        image: str = "",
        meta: dict[str, t.Any] | None = None,
        content: str = "",
    ):
        self.id = uuid4().hex
        self.section = section
        self.title = title
        self.description = description
        self.image = image
        self.url = url
        self.meta = meta or {}
        self.content = content


class SearchPageData(t.TypedDict):
    """
    SearchData represents the data structure for search functionality.
    It contains a mapping of page identifiers to their searchable content.
    """
    title: str
    content: str
    section: str
    url: str

TSearchData = dict[str, SearchPageData]
