import typing as t
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


__all__ = (
    "TMetadata",
    "PageRef",
    "TSearchPageData",
    "NavItem",
    "PageData",
    "SiteData",
)


TMetadata = dict[str, t.Any]


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
    url: str
    section_title: str
    section_url: str
    meta: dict[str, t.Any]
    source: str
    content: str
    filepath: Path | None = None
    prev: PageRef | None = None
    next: PageRef | None = None
    search_data: TSearchData | None = None
    toc: list[dict[str, t.Any]]
    parents: tuple[str, ...]  # IDs of parent items

    def __init__(
        self,
        *,
        url: str = "",
        section_title: str = "",
        section_url: str = "",
        meta: dict[str, t.Any] | None = None,
        source: str = "",
        content: str = "",
        filepath: Path | None = None,
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
        meta.setdefault("id", slug or uuid4().hex)
        self.url = url
        self.section_title = section_title
        self.section_url = section_url
        self.meta = meta
        self.source = source
        self.content = content
        self.filepath = filepath
        self.toc = toc or []
        self.parents = parents

    @property
    def id(self) -> str:
        return self.meta["id"]

    @property
    def title(self) -> str:
        return self.meta.get("title", self.filepath.name if self.filepath else "")

    @property
    def icon(self) -> str:
        return self.meta.get("icon", "")

    @property
    def view(self) -> str:
        return self.meta.get("view", "page.jinja")

    def __repr__(self) -> str:
        return f"<Page {self.url}>"

    def render_metadata(self, **kwargs) -> str:
        from . import utils

        return utils.render_metadata(self.meta, **kwargs)


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
