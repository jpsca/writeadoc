import typing as t
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import uuid4


__all__ = (
    "TUserSection",
    "TUserPages",
    "PageRef",
    "TSearchPageData",
    "NavItem",
    "PageData",
    "SiteData",
)


class TUserSection(t.TypedDict):
    title: str
    path: str
    icon: str | None
    pages: "TUserPages"


TUserPages = Sequence[str | TUserSection]


class TSearchPageData(t.TypedDict):
    """
    SearchData represents the data structure for search functionality.
    It contains a mapping of page identifiers to their searchable content.
    """

    title: str
    content: str
    section: str
    url: str


TSearchData = dict[str, TSearchPageData]


class NavItem:
    id: str
    title: str
    url: str
    icon: str
    pages: "list[NavItem]"
    # Whether the item is closed (collapsed)
    closed: bool = False

    def __init__(
        self,
        *,
        id: str = "",
        title: str,
        url: str = "",
        icon: str = "",
        pages: list["NavItem"] | None = None,
        closed: bool = False,
    ):
        slug = (
            url.strip()
            .replace("docs/", "")
            .replace("/", "-")
            .replace(" ", "-")
            .strip("-")
        )
        self.id = id or slug or uuid4().hex
        self.title = title
        self.url = url
        self.icon = icon
        self.pages = pages or []
        self.closed = closed

    def dict(self) -> dict[str, t.Any]:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "icon": self.icon,
            "pages": [p.dict() for p in self.pages],
        }

    def __repr__(self) -> str:
        return str(self.dict())


@dataclass
class PageRef:
    id: str
    title: str
    url: str
    section: str


class PageData:
    id: str
    title: str
    url: str
    icon: str
    view: str
    section_title: str
    section_url: str
    meta: dict[str, t.Any]
    content: str
    prev: PageRef | None = None
    next: PageRef | None = None
    search_data: TSearchData | None = None
    toc: list[dict[str, t.Any]]
    # IDs of parent items
    parents: tuple[str, ...]

    def __init__(
        self,
        *,
        section_title: str = "",
        section_url: str = "",
        id: str = "",
        title: str,
        url: str = "",
        icon: str = "",
        meta: dict[str, t.Any] | None = None,
        view: str = "",
        content: str = "",
        toc: list[dict[str, t.Any]] | None = None,
        parents: tuple[str, ...] = (),
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
        self.section_title = section_title
        self.section_url = section_url
        self.title = title
        self.url = url
        self.icon = icon
        self.view = view or meta.get("view", "page.jinja")
        self.meta = meta
        self.content = content
        self.toc = toc or []
        self.parents = parents

    def __repr__(self) -> str:
        return f"<Page {self.url}>"


class SiteData:
    name: str = "WriteADoc"
    version: str = "1.0"
    base_url: str = ""
    lang: str = "en"
    archived: bool = False
    pages: list[PageData]
    nav: list[NavItem]

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
        self.nav = []

    def __getattr__(self, name: str) -> t.Any:
        return None
