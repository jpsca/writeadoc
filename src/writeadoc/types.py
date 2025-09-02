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


class PageData:
    id: str
    section: SectionRef
    title: str
    url: str
    view: str
    meta: dict[str, t.Any]
    content: str
    prev: PageRef | None = None
    next: PageRef | None = None
    pages: list["PageData"]

    def __init__(
        self,
        *,
        section: SectionRef,
        id: str = "",
        title: str,
        url: str = "",
        meta: dict[str, t.Any] | None = None,
        view: str = "page.jinja",
        content: str = "",
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
        self.url = url
        self.view = meta.get("view", view)
        self.meta = meta
        self.content = content
        self.pages = pages or []


class SiteData:
    name: str = "WriteADoc"
    version: str = "1.0"
    base_url: str = ""
    lang: str = "en"
    archived: bool = False
    pages: list[tuple[SectionRef, list[PageData]]]

    def __init__(self, **data: t.Any):
        for key, value in data.items():
            if key.startswith("_"):
                continue
            setattr(self, key, value)

        self.base_url = self.base_url or ""
        if self.base_url.endswith("/"):
            self.base_url = self.base_url.rstrip("/")

        self.archived = False
        self.pages = []

    def __getattr__(self, name: str) -> t.Any:
        return None


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
