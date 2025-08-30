import typing as t
from uuid import uuid4


class SiteMeta(t.TypedDict, total=False):
    name: str
    description: str
    image: str
    version: str
    base_url: str
    source_url: str
    help_url: str


class SectionRef(t.TypedDict):
    id: str
    title: str
    url: str


class PageRef(t.TypedDict):
    id: str
    title: str
    url: str



class TSiteData(t.TypedDict, total=False):
    name: str
    description: str
    image: str
    version: str
    base_url: str
    source_url: str
    help_url: str
    lang: str


DEFAULT_SITE_DATA = {
    "name": "WriteADoc",
    "description": "",
    "image": "/assets/images/opengraph.png",
    "version": "1.0",
    "base_url": "",
    "source_url": "",
    "help_url": "",
    "lang": "en",
    "archived": False,
}


class PageData:
    id: str
    section: SectionRef
    title: str
    url: str
    view: str
    description: str
    image: str
    meta: dict[str, t.Any]
    content: str
    prev: PageRef | None = None
    next: PageRef | None = None
    updated_at: str
    pages: list["PageData"]

    def __init__(
        self,
        *,
        section: SectionRef,
        id: str = "",
        title: str,
        url: str = "",
        description: str = "",
        image: str = "",
        meta: dict[str, t.Any] | None = None,
        view: str = "page.jinja",
        content: str = "",
        updated_at: str = "",
        pages: list["PageData"] | None = None,
    ):
        meta = meta or {}
        slug = (
            url.strip()
            .replace("docs/", "")
            .replace("/", "-")
            .replace(" ", "-")
            .strip("-")
        )
        self.id = id or slug or uuid4().hex
        self.section = section
        self.title = title
        self.description = description
        self.image = image
        self.url = url
        self.view = meta.get("view", view)
        self.meta = meta
        self.content = content
        self.updated_at = updated_at
        self.pages = pages or []


class SiteData:
    name: str
    description: str
    image: str
    version: str
    base_url: str
    source_url: str
    help_url: str
    lang: str
    archived: bool
    pages: list[tuple[SectionRef, list[PageData]]]

    def __init__(self, **data: t.Any):
        for key, value in DEFAULT_SITE_DATA.items():
            setattr(self, key, data.get(key, value))

        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")

        self.archived = False
        self.pages = []


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
