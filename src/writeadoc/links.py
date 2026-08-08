"""Validation of the internal links found in the markdown sources."""

import posixpath
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .types import PageData


__all__ = ("LinkWarning", "validate_links")


RX_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s[^)]*)?\)")
RX_ID = re.compile(r'\bid=["\']([^"\']+)["\']')
RX_EXTERNAL = re.compile(r"^(https?://|mailto:|tel:)")


@dataclass(frozen=True)
class LinkWarning:
    filename: str
    lineno: int
    message: str


def validate_links(
    pages: Sequence[PageData],
    *,
    content_root: Path,
    assets_dir: Path,
    build_dir: Path,
    root_dir: Path,
    prefix: str = "",
    is_main: bool = True,
) -> list[LinkWarning]:
    """Find broken internal links and anchors in the markdown sources of `pages`.

    Arguments:
        pages: The pages to validate.
        content_root: Folder the reported filenames are made relative to.
        assets_dir: The assets *source* folder, where `/assets/…` links are looked up.
        build_dir: The build folder, where generated files are looked up.
        root_dir: The project root, where source-relative paths are looked up.
        prefix: The URL prefix of the documentation, if any.
        is_main: Whether this is the main documentation rather than a variant.

    Returns:
        The warnings found, in source order.

    """
    page_urls = {page.url for page in pages}
    prefixed_folders = get_prefixed_folders(prefix=prefix, is_main=is_main)
    warnings: list[LinkWarning] = []

    for page in pages:
        if not page.source or not page.filepath:
            continue

        filename = str(page.filepath.relative_to(content_root))
        page_ids = set(RX_ID.findall(page.content)) if page.content else set()

        for lineno, line in enumerate(page.source.splitlines(), start=1):
            for match in RX_LINK.finditer(line):
                raw_url = match.group(2)
                url, _, anchor = raw_url.partition("#")

                # Anchor-only link: validate against page IDs
                if not url:
                    if anchor and page_ids and anchor not in page_ids:
                        warnings.append(
                            LinkWarning(filename, lineno, f"broken anchor: #{anchor}")
                        )
                    continue

                # Skip external links, mailto/tel, and llms.txt references
                if RX_EXTERNAL.match(url) or url.startswith("/llms.txt"):
                    continue

                url = resolve_url(
                    url,
                    page_url=page.url,
                    prefix=prefix,
                    prefixed_folders=prefixed_folders,
                )
                if url in page_urls:
                    continue

                if not target_exists(
                    url,
                    assets_dir=assets_dir,
                    build_dir=build_dir,
                    root_dir=root_dir,
                    prefix=prefix,
                ):
                    warnings.append(
                        LinkWarning(filename, lineno, f"broken link: {raw_url}")
                    )

    return warnings


def get_prefixed_folders(*, prefix: str, is_main: bool) -> tuple[str, ...]:
    """The top-level folders whose URLs carry the documentation prefix.

    Variants share the main site's `assets` folder, so only the main
    documentation prefixes it.
    """
    if not prefix:
        return ()
    return ("docs", "assets", "search") if is_main else ("docs", "search")


def resolve_url(
    url: str,
    *,
    page_url: str,
    prefix: str,
    prefixed_folders: tuple[str, ...],
) -> str:
    """Turn a markdown link target into an absolute, normalized site URL."""
    if not url.startswith("/"):
        # Resolve relative URLs against the page's own URL
        url = posixpath.normpath(f"{page_url.rstrip('/')}/{url}")
        if not url.startswith("/"):
            url = f"/{url}"
    elif prefixed_folders and not url.startswith(f"/{prefix}/"):
        # Markdown sources reference unprefixed paths; mirror `_add_prefix_to_urls`
        for folder in prefixed_folders:
            if url == f"/{folder}" or url.startswith(f"/{folder}/"):
                url = f"/{prefix}{url}"
                break

    # Ensure a trailing slash for page-like URLs (those without an extension)
    if "." not in url.split("/")[-1] and not url.endswith("/"):
        url = f"{url}/"
    return url


def target_exists(
    url: str,
    *,
    assets_dir: Path,
    build_dir: Path,
    root_dir: Path,
    prefix: str,
) -> bool:
    """Whether a resolved URL points at an existing asset or generated file."""
    # Assets are looked up in their source folder, as they may not be copied yet
    asset_url = url
    if prefix and asset_url.startswith(f"/{prefix}/assets/"):
        asset_url = asset_url[len(f"/{prefix}"):]
    if asset_url.startswith("/assets/"):
        return (assets_dir / asset_url[len("/assets/"):]).exists()

    return (build_dir / url.strip("/")).exists() or (root_dir / url.strip("/")).exists()
