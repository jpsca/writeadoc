import typing as t
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import uuid4


__all__ = (
    "TUserPage",
    "TUserSection",
    "TUserPages",
    "PageRef",
    "SearchPageData",
    "NavItem",
    "PageData",
    "SiteData",
)


class TUserPage(t.TypedDict):
    path: str
    icon: str | None


class TUserSection(t.TypedDict):
    title: str
    icon: str | None
    pages: "TUserPages"


TUserPages = Sequence[str | TUserPage | TUserSection]


@dataclass
class PageRef:
    id: str
    title: str
    url: str
    section: str


@dataclass
class SearchPageData:
    """
    SearchData represents the data structure for search functionality.
    It contains a mapping of page identifiers to their searchable content.
    """

    title: str
    content: str
    section: str
    url: str


TSearchData = dict[str, SearchPageData]


class NavItem:
    id: str
    title: str
    url: str
    icon: str
    pages: "list[NavItem]"

    def __init__(
        self,
        *,
        id: str = "",
        title: str,
        url: str = "",
        icon: str = "",
        pages: list["NavItem"] | None = None,
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


class PageData:
    id: str
    title: str
    url: str
    icon: str
    view: str
    section: str
    meta: dict[str, t.Any]
    content: str
    prev: PageRef | None = None
    next: PageRef | None = None
    search_data: TSearchData | None = None

    def __init__(
        self,
        *,
        section: str = "",
        id: str = "",
        title: str,
        url: str = "",
        icon: str = "",
        meta: dict[str, t.Any] | None = None,
        view: str = "page.jinja",
        content: str = "",
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
        self.icon = icon
        self.view = meta.get("view", view)
        self.meta = meta
        self.content = content

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
